"""Validate every strands-aws schema against its golden instance.

Run:  python3 validate_schemas.py        (needs: jsonschema)
Exit: 0 when every check prints PASS; 1 otherwise.

The golden instances are REAL: captured at spec-build time from
live offline tool I/O against examples/syllabus.json (course,
plan, quiz, today view, checkin log), from evidence/demo-run.json
(the demo receipt), from a fresh run_agent execution (the fresh
receipt), and from the strands-agents 1.63.0 SDK itself (the
generated toolSpecs). Schemas that do not validate their goldens
do not ship — that is the acceptance bar on the spec issue.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCHEMAS = HERE / "schemas"
GOLDEN = HERE / "golden"

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

FAILURES = []


def load(path: Path):
    return json.loads(path.read_text())


def registry() -> Registry:
    reg = Registry()
    for name in ("payloads", "tools", "receipt", "runtime",
                 "deployment", "endpoint"):
        doc = load(SCHEMAS / f"{name}.schema.json")
        reg = reg.with_resource(
            f"{name}.schema.json",
            Resource.from_contents(doc))
    return reg


def check(label: str, schema_doc: dict, instance, reg: Registry):
    v = Draft202012Validator(schema_doc, registry=reg)
    errors = sorted(v.iter_errors(instance), key=lambda e: e.path)
    if errors:
        FAILURES.append(label)
        print(f"FAIL {label}")
        for e in errors[:4]:
            print(f"     at {list(e.path)}: {e.message[:140]}")
    else:
        print(f"PASS {label}")


def ref(name: str, defn: str) -> dict:
    return {"$ref": f"{name}.schema.json#/$defs/{defn}"}


def main() -> int:
    reg = registry()
    payloads = load(SCHEMAS / "payloads.schema.json")
    tools = load(SCHEMAS / "tools.schema.json")
    receipt_schema = load(SCHEMAS / "receipt.schema.json")
    runtime = load(SCHEMAS / "runtime.schema.json")
    deployment = load(SCHEMAS / "deployment.schema.json")
    endpoint = load(SCHEMAS / "endpoint.schema.json")

    course = load(GOLDEN / "course.json")
    plan = load(GOLDEN / "plan.json")
    quiz = load(GOLDEN / "quiz.json")
    today = load(GOLDEN / "today_view.json")
    checkin = load(GOLDEN / "checkin_log.json")
    demo_receipt = load(GOLDEN / "demo-receipt.json")
    fresh_receipt = load(GOLDEN / "fresh-receipt.json")
    toolspecs = load(GOLDEN / "toolspecs.json")

    # 1 · payloads vs their goldens
    check("payload CourseDocument vs golden course",
          ref("payloads", "CourseDocument"), course, reg)
    check("payload PlanDocument vs golden plan",
          ref("payloads", "PlanDocument"), plan, reg)
    check("payload QuizDocument vs golden quiz",
          ref("payloads", "QuizDocument"), quiz, reg)
    check("payload TodayView vs golden today view",
          ref("payloads", "TodayView"), today, reg)
    check("payload CheckinLog vs golden checkin log",
          ref("payloads", "CheckinLog"), checkin, reg)

    # 2 · tool wire inputs + decoded outputs vs live offline I/O
    wire = {
        "FetchSyllabusEvidence": (
            {"ref": "examples/syllabus.json"},
            json.loads((GOLDEN / "fresh-receipt.json").read_text())
            .get("evidence_set", {}).get("items", [])),
        "MakePlan": ({"course_json": json.dumps(course)}, plan),
        "MakeQuiz": ({"course_json": json.dumps(course), "week": 1},
                     quiz),
        "Replan": ({"plan_json": json.dumps(plan), "missed_week": 1},
                   plan),
        "GetTodayView": ({"plan_json": json.dumps(plan)}, today),
        "AdjustTimeBudget": (
            {"plan_json": json.dumps(plan), "minutes_per_day": 45},
            plan),
        "CheckinSession": (
            {"log_json": json.dumps({"entries": []}), "week": 1,
             "session_index": 0, "status": "done"}, checkin),
    }
    for name, (win, wout) in wire.items():
        check(f"tool {name}Input vs wire instance",
              ref("tools", f"{name}Input"), win, reg)
        check(f"tool {name}Output vs decoded golden",
              ref("tools", f"{name}Output"), wout, reg)
    # the generated toolSpecs agree with the hand-written inputs:
    # same property names, same required set, per tool
    spec_map = {
        "fetch_syllabus_evidence": "FetchSyllabusEvidence",
        "make_plan": "MakePlan", "make_quiz": "MakeQuiz",
        "replan": "Replan", "get_today_view": "GetTodayView",
        "adjust_time_budget": "AdjustTimeBudget",
        "checkin_session": "CheckinSession",
    }
    for sdk_name, defn in spec_map.items():
        gen = toolspecs[sdk_name]["inputSchema"]["json"]
        mine = tools["$defs"][f"{defn}Input"]
        same = (set(gen["properties"]) == set(mine["properties"])
                and set(gen.get("required", []))
                == set(mine.get("required", [])))
        print(("PASS " if same else "FAIL ")
              + f"toolSpec parity {sdk_name} (generated == hand-written)")
        if not same:
            FAILURES.append(f"toolSpec parity {sdk_name}")

    # 3 · receipts: demo golden, fresh golden, live extension
    check("receipt vs demo-run golden", receipt_schema,
          demo_receipt, reg)
    check("receipt vs fresh offline golden", receipt_schema,
          fresh_receipt, reg)
    live = dict(fresh_receipt)
    live.update({
        "execution_class": "live-production",
        "model": {"provider": "bedrock",
                  "model_id":
                      "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
                  "sdk_version": "1.63.0"},
        "tool_trace": [{
            "tool": "fetch_syllabus_evidence", "order": 0,
            "output_sha256": hashlib.sha256(b"golden").hexdigest()}],
        "fail_closed": False,
    })
    check("receipt live-extension instance", receipt_schema, live,
          reg)

    # 4 · runtime + endpoint shapes
    check("runtime InvocationRequest vs golden ask",
          ref("runtime", "InvocationRequest"),
          {"prompt": "Plan my course.",
           "request": {"id": "golden-1", "action": "plan",
                       "artifact": {"kind": "syllabus",
                                    "ref": "examples/syllabus.json"}}},
          reg)
    check("runtime PingResponse example",
          ref("runtime", "PingResponse"),
          {"status": "Healthy", "time_of_last_update": 1762214400},
          reg)
    check("endpoint PlanRequest vs golden course",
          ref("endpoint", "PlanRequest"), {"syllabus": course}, reg)
    check("endpoint PlanResponse vs fresh receipt",
          ref("endpoint", "PlanResponse"), fresh_receipt, reg)
    check("endpoint HealthResponse example",
          ref("endpoint", "HealthResponse"),
          {"status": "ok", "strands_agent_available": True,
           "deployment": True,
           "model_id":
               "us.anthropic.claude-sonnet-4-5-20250929-v1:0"}, reg)

    # 5 · deployment: example config + IAM structure
    config = load(HERE / "deployment" / "config.example.json")
    check("deployment config.example vs DeploymentConfig",
          ref("deployment", "DeploymentConfig"), config, reg)
    policy = load(HERE / "deployment" / "iam-policy.json")
    wild_actions = [a for s in policy["Statement"]
                    for a in s["Action"] if a == "*" or a.endswith(":*")]
    wild_resources = [r for s in policy["Statement"]
                      for r in s["Resource"] if r == "*"]
    ok = not wild_actions and not wild_resources
    print(("PASS " if ok else "FAIL ")
          + "IAM policy: no wildcard actions, no bare-wildcard resources "
            f"({len(policy['Statement'])} statements)")
    if not ok:
        FAILURES.append("IAM wildcards")

    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILURE(S): {FAILURES}")
        return 1
    print("ALL SCHEMA VALIDATIONS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
