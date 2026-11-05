"""Consumption kind + named gap metric (owner fix order 2026-11-03).

Per-call usage of record is distinct from activity-proxy dispatch
counts: the usage-series builder gains kind "consumption" from per-call
usage records (ops/3l0/intake.jsonl usage{tokens_in,tokens_out} +
routed-dispatch record usage{} blocks), and every routed call WITHOUT
a usage value is counted in pack.consumption_gap - named, never
silently excluded.
"""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _builder():
    spec = importlib.util.spec_from_file_location(
        "quota_usage_series", ROOT / "scripts/quota_usage_series.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _fixture(tmp_path):
    def w(rel, text):
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    w("ops/quota/quota-usage.json", "{}")
    w("ops/challenge/desk-feed.json", json.dumps({"traversals": [
        {"provider_usage": [{"session_id": "sess-1", "usage": {
            "value": 77, "unit": "tokens", "match": "exact",
            "status": "established", "source": "desk-feed exact usage"}},
         {"session_id": "sess-waived", "usage": {"value": None, "unit": None,
            "match": None, "status": "waived", "source": "desk-feed",
            "note": "Pre-mandate shared bucket usage is unrecoverable."}},
         {"session_id": "sess-fault", "usage": {"value": None, "unit": None,
            "match": None, "status": "fault", "source": "desk-feed",
            "note": "Post-mandate dispatch stamp is missing."}},
         {"session_id": "sess-pending", "usage": {"value": None, "unit": None,
            "match": None, "status": "pending", "source": "desk-feed",
            "note": "Awaiting usage carrier."}},
         {"session_id": "sess-activity", "usage": {"value": 4, "unit": "sessions",
            "match": "activity-proxy", "status": "activity-only",
            "source": "desk-feed", "note": "Session count only."}}]}
    ]}))
    w("ops/quota/allocation-plan.json", "{}")
    w("ops/quota/rate-limit-events.json", "{}")
    w("ops/tracking/nested-family.json", json.dumps({"providers": [
        {"provider": "nestedprov", "models": [
            {"model": "nested-model", "tasks": [
                {"ts": "2026-11-01T00:00:00Z", "dispatch_id": "d-nested",
                 "role": "reviewer", "task_class": "test", "moniker": "participant-nested"}]}]},
        {"provider": "deepseek", "models": [
            {"model": "deepseek-chat", "tasks": [
                {"ts": "2026-11-02T00:00:00Z", "dispatch_id": "d1",
                 "role": "builder", "task_class": "implementation",
                 "moniker": "participant-deepseek", "run_id": "101"}]}]},
        {"provider": "gemini", "models": [
            {"model": "gemini-2.5-pro", "tasks": [
                {"ts": "2026-11-02T04:00:00Z", "dispatch_id": "d5",
                 "role": "reviewer", "task_class": "review",
                 "moniker": "participant-gemini", "run_id": "105"}]}]},
        {"provider": "session-provider", "models": [
            {"model": "session-model", "tasks": [
                {"session_id": "sess-1",
                 "role": "reviewer", "task_class": "session-review",
                 "moniker": "participant-session"}]}]},
        {"provider": "waived-provider", "models": [
            {"model": "waived-model", "tasks": [
                {"session_id": "sess-waived",
                 "role": "reviewer", "task_class": "pre-mandate-review",
                 "moniker": "participant-waived"}]}]},
        {"provider": "fault-provider", "models": [
            {"model": "fault-model", "tasks": [
                {"session_id": "sess-fault",
                 "role": "builder", "task_class": "missing-stamp",
                 "moniker": "participant-fault"}]}]},
        {"provider": "pending-provider", "models": [
            {"model": "pending-model", "tasks": [
                {"session_id": "sess-pending",
                 "role": "planner", "task_class": "awaiting-usage",
                 "moniker": "participant-pending"}]}]},
        {"provider": "mistral", "models": [
            {"model": "mistral-large", "tasks": [
                {"ts": "2026-11-02T02:00:00Z", "dispatch_id": "d3",
                 "role": "builder", "task_class": "no-usage-surface",
                 "moniker": "participant-mistral"}]}]},
        {"provider": "activity-provider", "models": [
            {"model": "activity-model", "tasks": [
                {"session_id": "sess-activity", "role": "planner",
                 "task_class": "session-activity", "moniker": "participant-activity"}]}]}
    ]}))
    w("ops/quota/registry.json", '{"services": []}')
    # 3L0 intake: one stamped call, one null-usage call, one
    # no-usage-surface call, one CI row (excluded from the denominator)
    rows = [
        {"dispatch_id": "d1", "ts": "2026-11-02T00:00:00Z",
         "provider": "deepseek", "model": "deepseek-chat",
         "quota": {"pool": "deepseek", "slice": None},
         "usage": {"tokens_in": 100, "tokens_out": 50}},
        {"dispatch_id": "d2", "ts": "2026-11-02T01:00:00Z",
         "provider": "cohere", "model": "command-r",
         "usage": {"tokens_in": None, "tokens_out": None}},
        {"dispatch_id": "d3", "ts": "2026-11-02T02:00:00Z",
         "provider": "mistral", "model": "mistral-large",
         "usage": {"status": "no-usage-surface"}},
        {"dispatch_id": "d4", "ts": "2026-11-02T03:00:00Z",
         "provider": "github-actions", "model": "ci",
         "usage": {"tokens_in": 5, "tokens_out": 5}},
    ]
    w("ops/3l0/intake.jsonl", "\n".join(json.dumps(r) for r in rows) + "\n")
    # one experiment record carrying a measured native-unit usage{};
    # its dispatch_id also appears in the intake corpus shape (dedupe
    # is by dispatch_id across sources)
    w("experiments/doe/routed-dispatch/records/d1.json", json.dumps({
        "dispatch_id": "d1", "ts": "2026-11-02T00:00:00Z",
        "provider": "deepseek", "model": "deepseek-chat",
        "quota": {"pool": "deepseek", "slice": "winning"}}))
    w("experiments/doe/routed-dispatch/stamps/s1.json", json.dumps({
        "dispatch_id": "d5", "ts": "2026-11-02T04:00:00Z",
        "provider": "gemini", "model": "gemini-2.5-pro",
        "quota": {"pool": "gemini", "slice": "repo-development"},
        "usage": {"status": "measured", "unit": "tokens", "value": 30,
                  "tokens_in": 20, "tokens_out": 10}}))
    return tmp_path


def test_consumption_series_and_gap(tmp_path):
    pack = _builder().build(str(_fixture(tmp_path)))
    cons = [s for rows in pack["axes"].values() for s in rows
            if s["kind"] == "consumption"]
    assert cons, "expected consumption series from stamped records"
    prov = {s["key"]: s for s in pack["axes"]["provider"]
            if s["kind"] == "consumption"}
    assert prov["deepseek::consumption"]["points"] == [
        {"t": "2026-11-02T00:00:00Z", "v": 150}]
    assert prov["gemini::consumption"]["points"][-1]["v"] == 30
    model = {s["key"]: s for s in pack["axes"]["model"]
             if s["kind"] == "consumption"}
    assert "deepseek-chat::consumption" in model
    gap = pack["consumption_gap"]
    # denominator: d1, d2, d3, d5 + nested carrier = 5 (CI excluded)
    assert gap["routed_calls"] == 5
    assert gap["usage_stamped"] == 2
    assert gap["unstamped"] == 3
    assert gap["causes"] == {"no-usage-record": 2, "no-usage-surface": 1}
    assert gap["by_provider"]["cohere"]["unstamped"] == 1
    assert gap["by_provider"]["nestedprov"]["calls"] == 1


def test_activity_proxy_unchanged_by_consumption_pass(tmp_path):
    pack = _builder().build(str(_fixture(tmp_path)))
    proxy = [s for s in pack["axes"]["model"] if s["kind"] == "activity-proxy"]
    assert proxy, "activity-proxy model series must still be produced"
    assert all(s["kind"] != "consumption" for s in proxy)


def test_graphs_page_renders_named_gap():
    html = (ROOT / "apps/tribute-dashboard/quota-graphs.html").read_text()
    assert "consumption_gap" in html
    assert "UNMEASURED" in html
    assert "consumption — per-call usage of record" in html


def test_task_tree_joins_usage_by_dispatch_and_preserves_role_and_pool(tmp_path):
    pack = _builder().build(str(_fixture(tmp_path)))
    tree = pack["task_tree"]
    assert tree["schema"] == "quota.task-tree/v1"
    deepseek = next(p for p in tree["providers"] if p["provider"] == "deepseek")
    model = next(m for m in deepseek["models"] if m["model"] == "deepseek-chat")
    role = next(r for r in model["roles"] if r["role"] == "builder")
    participant = role["participants"][0]
    task = participant["tasks"][0]
    assert task["dispatch_id"] == "d1"
    assert task["usage"]["status"] == "established"
    assert task["usage"]["value"] == 150 and task["usage"]["unit"] == "tokens"
    assert task["quota"] == {"pool": "deepseek", "slice": "winning"}
    gemini = next(p for p in tree["providers"] if p["provider"] == "gemini")
    gtask = gemini["models"][0]["roles"][0]["participants"][0]["tasks"][0]
    assert gtask["usage"]["value"] == 30
    assert gtask["quota"]["slice"] == "repo-development"
    gap = next(p for p in tree["providers"] if p["provider"] == "nestedprov")
    ntask = gap["models"][0]["roles"][0]["participants"][0]["tasks"][0]
    assert ntask["usage"]["status"] == "NOT_ESTABLISHED"
    assert ntask["usage"]["value"] is None
    session_provider = next(p for p in tree["providers"] if p["provider"] == "session-provider")
    stask = session_provider["models"][0]["roles"][0]["participants"][0]["tasks"][0]
    assert stask["attribution"] == "session_id"
    assert stask["usage"]["value"] == 77 and stask["usage"]["status"] == "established"
    waived_provider = next(p for p in tree["providers"] if p["provider"] == "waived-provider")
    wtask = waived_provider["models"][0]["roles"][0]["participants"][0]["tasks"][0]
    assert wtask["usage"]["status"] == "waived"
    assert "unrecoverable" in wtask["usage"]["note"]
    fault_provider = next(p for p in tree["providers"] if p["provider"] == "fault-provider")
    ftask = fault_provider["models"][0]["roles"][0]["participants"][0]["tasks"][0]
    assert ftask["usage"]["status"] == "fault"
    pending_provider = next(p for p in tree["providers"] if p["provider"] == "pending-provider")
    ptask = pending_provider["models"][0]["roles"][0]["participants"][0]["tasks"][0]
    assert ptask["usage"]["status"] == "pending"
    mistral = next(p for p in tree["providers"] if p["provider"] == "mistral")
    mtask = mistral["models"][0]["roles"][0]["participants"][0]["tasks"][0]
    assert mtask["usage"]["status"] == "no-usage-surface"
    activity_provider = next(p for p in tree["providers"] if p["provider"] == "activity-provider")
    atask = activity_provider["models"][0]["roles"][0]["participants"][0]["tasks"][0]
    assert atask["usage"]["status"] == "activity-only"
    assert atask["usage"]["match"] == "activity-proxy" and atask["usage"]["value"] == 4
    assert tree["generated_at"] == pack["generated_at"]
    assert tree["grouping"] == "provider -> model (verbatim) -> role (verbatim) -> participant (moniker) -> tasks"
    assert tree["coverage"]["tasks"] == 9
    assert tree["coverage"]["established"] == 3
    assert tree["coverage"]["activity_only"] == 1
    assert tree["coverage"]["waived"] == 1
    assert tree["coverage"]["fault"] == 1
    assert tree["coverage"]["pending"] == 1
    assert tree["coverage"]["no_usage_surface"] == 1
    assert tree["coverage"]["not_established"] == 1
