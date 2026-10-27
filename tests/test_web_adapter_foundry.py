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
    # Probing = finding the DOMs from the request: discovery leads.
    assert [p["id"] for p in plan[:3]] == ["request-inventory", "dom-attribution",
                                           "dom-data-source"]
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


BRIEF = {
    "target_id": "example-shop", "target": "https://shop.example.com/catalog",
    "purpose": "api-extraction", "side_effect": "read", "probe_budget": 24,
    "device_class": "b160v-on-device",
    "authorization": {"basis": "operator account", "scope_domains": ["shop.example.com"],
                      "state_changing": False},
    "surfaces": ["github-issue", "cli"], "evidence_expectation": "reproduced",
    "submitter": "inventory{atlas}",
}


def test_intake_validates_authorization_and_scope():
    assert waf.validate_brief(BRIEF) == []
    bad = dict(BRIEF, authorization={"basis": "x", "scope_domains": ["other.example"]})
    assert any("outside authorization.scope_domains" in e for e in waf.validate_brief(bad))
    nobasis = dict(BRIEF, authorization={"scope_domains": ["shop.example.com"]})
    assert any("basis" in e for e in waf.validate_brief(nobasis))
    write = dict(BRIEF, side_effect="write")
    assert any("state_changing" in e for e in waf.validate_brief(write))


def test_intake_plan_maps_purpose_to_taxonomy_and_b160v_law():
    tax = waf.load_taxonomy()
    plan = waf.plan_from_brief(BRIEF, tax)
    cats = {s["category"].split("/")[0] for s in plan["stack"]}
    assert cats == {"capture-and-recon", "contract-synthesis", "verification"}
    assert plan["registry_skeleton"]["operations"][0]["operation_id"] == "example-shop.discover"
    assert plan["transports"][:2] == ["cli", "stdin-jsonl"]
    # B160V law: nothing Chromium-class is assigned on-device in a data-extraction plan
    plan2 = waf.plan_from_brief(dict(BRIEF, purpose="data-extraction"), tax)
    sites = {s["repo"]: s["execution_site"] for s in plan2["stack"]}
    assert sites["fathyb/carbonyl"].startswith("remote-service")
    remote = waf.plan_from_brief(dict(BRIEF, purpose="monitoring", device_class="remote-service"), tax)
    assert "sse" in remote["transports"]


def test_intake_via_jsonl_builtin():
    out = waf.handle_request({"id": "9", "operation": "foundry.intake",
                              "input": {"brief": BRIEF}}, reg())
    assert out["ok"] and out["data"]["target_id"] == "example-shop"
    out = waf.handle_request({"id": "10", "operation": "foundry.intake",
                              "input": {"brief": {"target_id": "x"}}}, reg())
    assert not out["ok"] and out["error"]["code"] == "bad_brief"


ISSUE_BODY = """### Target ID

example-shop

### Target URL or domain

https://shop.example.com/catalog

### Purpose

api-extraction

### Authorization basis

operator account

### Scope domains

shop.example.com

### Side effect

read

### State-changing authorization

no

### Probe budget

24

### Execution venue

b160v-on-device

### Surfaces requested

github-issue, cli

### Evidence expectation

reproduced

### Submitter Role{Moniker}

inventory{atlas}

### Notes for the dispatcher

_No response_
"""


def test_issue_form_parses_into_the_same_brief():
    brief = waf.parse_issue_form(ISSUE_BODY)
    assert brief == BRIEF  # identical to the hand-written JSON brief
    assert waf.validate_brief(brief) == []


def test_issue_form_write_requires_checked_box():
    body = ISSUE_BODY.replace("### Side effect\n\nread", "### Side effect\n\nwrite")
    brief = waf.parse_issue_form(body)
    assert brief["authorization"]["state_changing"] is False
    assert any("state_changing" in e for e in waf.validate_brief(brief))
    yes = body.replace("### State-changing authorization\n\nno",
                       "### State-changing authorization\n\nyes")
    assert waf.parse_issue_form(yes)["authorization"]["state_changing"] is True
    assert waf.validate_brief(waf.parse_issue_form(yes)) == []
    # Legacy v1 checkbox rendering still parses (issues filed from it exist).
    legacy = body.replace("### State-changing authorization\n\nno",
                          "### State-changing authorization\n\n"
                          "- [X] This brief authorizes state-changing (write) operations on the target")
    assert waf.parse_issue_form(legacy)["authorization"]["state_changing"] is True


def test_issue_form_out_of_scope_domain_is_refused():
    body = ISSUE_BODY.replace("### Scope domains\n\nshop.example.com",
                               "### Scope domains\n\nother.example")
    assert any("outside authorization.scope_domains" in e
               for e in waf.validate_brief(waf.parse_issue_form(body)))


def test_render_plan_markdown_names_the_stack():
    md = waf.render_plan_markdown(waf.plan_from_brief(BRIEF, waf.load_taxonomy()))
    assert "example-shop" in md and "rever-browser" in md and "schemathesis" in md.lower()


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


# ------------------------------------------------- template submission (2026)

CANONICAL_FORM_BODY = """### Target ID

example-shop

### Target URL or domain

https://shop.example.com/catalog

### Purpose

api-extraction

### Authorization basis

Operator owns this storefront account; read-only catalogue access for price monitoring.

### Scope domains

shop.example.com

### Side effect

read

### State-changing authorization

no

### Probe budget

24

### Execution venue

remote-service

### Surfaces requested

github-issue, cli, jsonl, chat, http-facade

### Evidence expectation

reproduced

### Submitter Role{Moniker}

inventory{atlas}

### Notes for the dispatcher

_No response_
"""


def test_submission_template_fields_validate():
    assert waf.validate_brief(BRIEF) == []
    assert any("surfaces" in e for e in waf.validate_brief(dict(BRIEF, surfaces=["smoke-signal"])))
    assert any("surfaces" in e for e in waf.validate_brief(dict(BRIEF, surfaces=[])))
    assert any("evidence_expectation" in e for e in
               waf.validate_brief(dict(BRIEF, evidence_expectation="vibes")))
    assert any("submitter" in e for e in waf.validate_brief(dict(BRIEF, submitter="atlas")))
    assert any("submitter" in e for e in waf.validate_brief(dict(BRIEF, submitter="{atlas}")))
    minimal = {k: v for k, v in BRIEF.items()
               if k not in ("surfaces", "evidence_expectation", "submitter")}
    assert waf.validate_brief(minimal) == []  # optional on every surface
    plan = waf.plan_from_brief(minimal, waf.load_taxonomy())
    assert plan["surfaces"] == list(waf.SURFACES)
    assert plan["evidence_expectation"] == "reproduced" and plan["submitter"] is None


def test_canonical_template_same_brief_every_surface():
    canonical = json.loads((ROOT / "ops" / "web_adapter_foundry" / "examples"
                            / "target-brief.example.json").read_text())
    assert waf.validate_brief(canonical) == []
    parsed = waf.parse_issue_form(CANONICAL_FORM_BODY)  # GitHub-form rendering
    assert parsed == canonical  # ... parses back to the exact canonical brief
    assert (waf.plan_from_brief(parsed, waf.load_taxonomy())
            == waf.plan_from_brief(canonical, waf.load_taxonomy()))


def test_plan_markdown_carries_submission_fields():
    md = waf.render_plan_markdown(waf.plan_from_brief(BRIEF, waf.load_taxonomy()))
    assert "inventory{atlas}" in md and "github-issue" in md and "reproduced" in md
