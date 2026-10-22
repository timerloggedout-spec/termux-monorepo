"""Web Adapter Foundry core tests — stdlib pytest, no network."""
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ops.web_adapter_foundry import waf  # noqa: E402

EXAMPLE = ROOT / "ops" / "web_adapter_foundry" / "examples" / "example.registry.json"


def reg():
    return json.loads(EXAMPLE.read_text())


def test_catalog_is_well_formed_and_covers_the_stack():
    cat = waf.load_catalog()
    repos = {p["repo"] for p in cat["projects"]}
    for required in ("greekr4/rever-browser", "jackwener/opencli", "morluto/rea",
                     "alufers/mitmproxy2swagger", "j4k0xb/webcrack",
                     "curlconverter/curlconverter", "microsoft/playwright-mcp",
                     "schemathesis/schemathesis", "alexgaoth/awesome-reverse-engineered"):
        assert required in repos
    for p in cat["projects"]:
        assert p["role"] and p["boundary"] and p["capabilities"]


def test_example_registry_validates():
    assert waf.validate_registry(reg()) == []


def test_registry_rejects_write_with_automatic_fallback():
    bad = reg()
    bad["operations"][2]["fallback"] = {"allowed": ["browser-context-request"]}
    errs = waf.validate_registry(bad)
    assert any("write operations must not declare automatic fallback" in e for e in errs)


def test_registry_rejects_direct_http_without_allowlist():
    bad = reg()
    del bad["operations"][1]["allowlist"]
    assert any("allowlist" in e for e in waf.validate_registry(bad))


def test_envelope_rules_and_credential_refusal():
    assert waf.validate_envelope({"id": "1", "operation": "reports.list"}) == []
    assert waf.validate_envelope({"operation": "x"})  # missing id
    errs = waf.validate_envelope({"id": "1", "operation": "x",
                                  "input": {"password": "hunter2"}})
    assert any("credentials" in e for e in errs)


def test_promotion_state_machine():
    assert waf.can_promote("modeled", "reproduced")[0]
    assert not waf.can_promote("modeled", "stable")[0]  # no skipping
    assert waf.can_promote("stable", "degraded")[0]
    assert waf.can_promote("degraded", "modeled")[0]    # repair re-entry
    assert not waf.can_promote("degraded", "verified")[0]


def test_probe_plan_is_ordered_and_write_annotated():
    ops = {o["operation_id"]: o for o in reg()["operations"]}
    plan = waf.plan_probes(ops["reports.list"])
    assert plan[0]["id"] == "exact-replay"
    assert plan[-1]["id"] == "controlled-error"
    write_plan = waf.plan_probes(ops["reports.export"])
    assert all("note" in p for p in write_plan)
    direct_plan = waf.plan_probes(ops["reports.get"])
    assert all(p["id"] != "browser-vs-direct" for p in direct_plan)


def test_handle_builtin_and_echo_and_unpromoted():
    r = reg()
    assert waf.handle_request({"id": "1", "operation": "foundry.ping"}, r)["data"]["pong"]
    out = waf.handle_request({"id": "2", "operation": "reports.list",
                              "input": {"limit": 5}}, r)
    assert out["ok"] and out["data"]["echo"] == {"limit": 5}
    out = waf.handle_request({"id": "3", "operation": "reports.export"}, r)
    assert not out["ok"] and out["error"]["code"] == "not_promoted"
    out = waf.handle_request({"id": "4", "operation": "nope.nope"}, r)
    assert out["error"]["code"] == "unknown_operation"
    out = waf.handle_request({"id": "5", "operation": "foundry.promote",
                              "input": {"from": "modeled", "to": "stable"}}, r)
    assert not out["ok"] and out["error"]["code"] == "bad_transition"


def test_direct_http_allowlist_enforced_without_network():
    r = reg()
    out = waf.handle_request({"id": "1", "operation": "reports.get",
                              "input": {"url": "https://evil.example/x"}}, r)
    assert not out["ok"] and out["error"]["code"] == "not_allowlisted"


def test_taxonomy_folds_both_candidate_sets_exactly_once():
    tax = waf.load_taxonomy()
    repos = [n["repo"].lower() for n in tax["nodes"]]
    assert len(repos) == len(set(repos)) == 31
    both = {n["repo"] for n in tax["nodes"] if len(n["sources"]) == 2}
    assert both == {"greekr4/rever-browser", "jackwener/OpenCLI"}
    for n in tax["nodes"]:
        assert n["category_path"][0] == "web-reverse-engineering"
        assert n["category_path"][1] in tax["categories"]
    assert tax["umbrella"]["name"] == "connectors-tooling-abilities"
    for transport in ("stdin-jsonl", "cdp-websocket", "sse", "websocket", "http", "mcp"):
        assert transport in tax["transports"]


def test_taxonomy_placement_examples():
    tax = waf.load_taxonomy()
    assert waf.taxonomy_node(tax, "lightpanda-io/browser")["category_path"][-2:] == ["engines", "thin-from-scratch"]
    assert waf.taxonomy_node(tax, "h4ckf0r0day/obscura")["b160v_tier"].startswith("on-device")
    assert waf.taxonomy_node(tax, "nope/nope") is None


def test_sse_encode_and_event_bus():
    frame = waf.sse_encode({"ok": True}, event="result", event_id=7)
    assert frame.startswith("id: 7\nevent: result\ndata: ")
    assert frame.endswith("\n\n")
    bus = waf.EventBus()
    q = bus.subscribe()
    published = bus.publish({"n": 1}, event="result")
    assert q.get_nowait() == published and "id: 1" in published
    bus.unsubscribe(q)
    bus.publish({"n": 2})
    assert q.empty()


def test_jsonl_round_trip_stdout_is_protocol_only():
    inp = io.StringIO(
        '{"id":"a","operation":"foundry.ping"}\n'
        'not json\n'
        '{"id":"b","operation":"foundry.list_operations"}\n')
    outp = io.StringIO()
    waf.serve(reg(), inp, outp)
    lines = outp.getvalue().strip().splitlines()
    assert len(lines) == 3
    parsed = [json.loads(x) for x in lines]
    assert parsed[0]["ok"] and parsed[0]["id"] == "a"
    assert parsed[1]["error"]["code"] == "bad_json"
    assert "reports.list" in parsed[2]["data"]["operations"]
