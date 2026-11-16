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
    w("ops/challenge/desk-feed.json", "{}")
    w("ops/quota/allocation-plan.json", "{}")
    w("ops/quota/rate-limit-events.json", "{}")
    w("ops/tracking/nested-family.json", json.dumps({"providers": [
        {"provider": "nestedprov", "models": [
            {"model": "nested-model", "tasks": [
                {"ts": "2026-11-01T00:00:00Z", "dispatch_id": "d-nested"}]}]}]}))
    w("ops/quota/registry.json", '{"services": []}')
    # 3L0 intake: one stamped call, one null-usage call, one
    # no-usage-surface call, one CI row (excluded from the denominator)
    rows = [
        {"dispatch_id": "d1", "ts": "2026-11-02T00:00:00Z",
         "provider": "deepseek", "model": "deepseek-chat",
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
    w("experiments/doe/routed-dispatch/stamps/s1.json", json.dumps({
        "dispatch_id": "d5", "ts": "2026-11-02T04:00:00Z",
        "provider": "gemini", "model": "gemini-2.5-pro",
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
