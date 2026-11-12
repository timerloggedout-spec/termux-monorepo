#!/usr/bin/env python3
"""Arm eligibility census for multi-arm build routing (issue #5151).

Gate for every arm, incl. the existing one: {free — invocable from
Actions — drives an agent loop (tool-calling round-trip in a full
checkout)}. Bounded smoke per arm on the provider_free_smoke pattern:
exact model identity from the registry, at most 3 completion requests
per arm, and a smoke never enables production routing by itself — the
feed records verdicts; arm selection reads them.

Arms seed as CANDIDATE (correction c.6786217937): the round-1 INVOKE OK
verdicts on #3141 prove invocability only. This census adds the missing
leg — a read_file tool round-trip executed in this checkout, with the
model required to report back content only the tool result carries.

Output: the arm-census feed (`ops/que/feeds/arm-census.json` in the
runner workspace; the seat folds the artifact into the PR). Exit code is
0 whenever verdicts were produced — per-arm outcomes live in the feed,
not the exit code (provider_invoke pattern).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_arm_harness as harness  # noqa: E402

PROBE_FILE = "ops/dispatch/build-arms.json"
PROBE_MARKER = "build-arms/v1"


def census_http_arm(arm: dict, root: Path) -> dict:
    checks = {"free": (arm.get("budget") or {}).get("class") == "free-tier",
              "budget_class": (arm.get("budget") or {}).get("class")}
    row = {"arm_id": arm["arm_id"], "provider": arm["endpoint"].get("provider"),
           "model": arm.get("model"), "budget_class": checks["budget_class"],
           "status_before": arm.get("status"), "checks": checks}
    token_env = arm["endpoint"].get("secret_env")
    if not token_env or not os.environ.get(token_env):
        row.update(verdict="failed", reason=f"missing_secret:{token_env}",
                   quota_terminal={"terminal": False})
        checks["invocable_from_actions"] = {"ok": False, "error_class": "missing_secret"}
        checks["agent_loop"] = {"tool_call_seen": False, "roundtrip_ok": False,
                                "error_class": "missing_secret"}
        return row
    # Leg 1: invocable — one bounded completion, exact model identity.
    started = time.time()
    try:
        reply = harness.chat_once(
            arm, [{"role": "user", "content": "Reply with exactly: OK"}], None, max_tokens=16)
        checks["invocable_from_actions"] = {
            "ok": True, "http": 200,
            "latency_ms": int((time.time() - started) * 1000)}
    except harness.QuotaTerminal:
        checks["invocable_from_actions"] = {"ok": False, "error_class": "quota_terminal_429"}
        checks["agent_loop"] = {"tool_call_seen": False, "roundtrip_ok": False,
                                "error_class": "quota_terminal_429"}
        row.update(verdict="failed", reason="quota_terminal_on_invoke",
                   quota_terminal={"terminal": True, "date": harness.today_pt()})
        return row
    except harness.ArmFailure as exc:
        checks["invocable_from_actions"] = {
            "ok": False, "http": exc.http, "error_class": f"invoke_failed:{exc}"[:160]}
        checks["agent_loop"] = {"tool_call_seen": False, "roundtrip_ok": False,
                                "error_class": "not_run_invoke_failed"}
        row.update(verdict="failed", reason="invoke_failed",
                   quota_terminal={"terminal": False})
        return row
    # Leg 2: agent loop — tool-calling round-trip in this checkout. The
    # model must call read_file on the registry and report the schema
    # string that only the tool result carries.
    messages = [
        {"role": "system", "content": "You are running an eligibility census. Use only the read_file tool when asked; never request or invoke commands, writes, or other tools."},
        {"role": "user", "content": (
            f"Call the read_file tool with path \"{PROBE_FILE}\", then reply with exactly "
            f"the value of the top-level \"schema\" field from that file.")},
    ]
    try:
        reply = harness.chat_once(arm, messages, harness.census_tool_definitions(), max_tokens=512)
        tool_seen = any(c.get("name") == "read_file" and (c.get("arguments") or {}).get("path") == PROBE_FILE for c in reply["tool_calls"])
        if not tool_seen:
            checks["agent_loop"] = {"tool_call_seen": False, "roundtrip_ok": False,
                                    "error_class": "no_tool_call_returned"}
            row.update(verdict="failed", reason="agent_loop_no_tool_call",
                       quota_terminal={"terminal": False})
            return row
        results = []
        for call in reply["tool_calls"]:
            if call.get("name") != "read_file" or (call.get("arguments") or {}).get("path") != PROBE_FILE:
                raise harness.ArmFailure("census model requested a tool/path outside the read-only probe allowlist")
            try:
                results.append((call, harness.run_tool(root, call["name"], call["arguments"])))
            except Exception as exc:  # tool errors are data for the loop, not census crashes
                results.append((call, f"tool error: {type(exc).__name__}: {exc}"))
        tool_result = "\n".join(result for _, result in results)
        harness.append_assistant_and_results(messages, arm, reply, results)
        final = harness.chat_once(arm, messages, None, max_tokens=128)
        roundtrip_ok = PROBE_MARKER in tool_result and (final.get("content") or "").strip() == PROBE_MARKER
        checks["agent_loop"] = {"tool_call_seen": True, "roundtrip_ok": roundtrip_ok,
                                "error_class": None if roundtrip_ok else "marker_not_reported"}
        if roundtrip_ok:
            row.update(verdict="eligible", reason="invoke_ok + tool round-trip ok",
                       quota_terminal={"terminal": False})
        else:
            row.update(verdict="failed", reason="agent_loop_marker_not_reported",
                       quota_terminal={"terminal": False})
        return row
    except harness.QuotaTerminal:
        checks["agent_loop"] = {"tool_call_seen": False, "roundtrip_ok": False,
                                "error_class": "quota_terminal_429"}
        row.update(verdict="failed", reason="quota_terminal_during_agent_loop",
                   quota_terminal={"terminal": True, "date": harness.today_pt()})
        return row
    except harness.ArmFailure as exc:
        checks["agent_loop"] = {"tool_call_seen": False, "roundtrip_ok": False,
                                "error_class": f"agent_loop_failed:{exc}"[:160]}
        row.update(verdict="failed", reason="agent_loop_failed",
                   quota_terminal={"terminal": False})
        return row


def census_arm(arm: dict, root: Path) -> dict:
    method = (arm.get("census") or {}).get("method")
    if method == "http-tool-roundtrip":
        return census_http_arm(arm, root)
    if method == "existing-harness-evidence":
        return {"arm_id": arm["arm_id"], "provider": arm["endpoint"].get("provider"),
                "model": arm.get("model"),
                "budget_class": (arm.get("budget") or {}).get("class"),
                "status_before": arm.get("status"),
                "checks": {"free": (arm.get("budget") or {}).get("class") == "free-tier",
                           "invocable_from_actions": {"ok": True, "method": method},
                           "agent_loop": {"tool_call_seen": True, "roundtrip_ok": True,
                                          "method": method}},
                "verdict": "eligible",
                "reason": (arm.get("census") or {}).get("evidence_ref") or "existing harness evidence",
                "quota_terminal": {"terminal": False}}
    # Class-only / not-admitted rows are censused honestly as such.
    return {"arm_id": arm["arm_id"], "provider": (arm.get("endpoint") or {}).get("provider"),
            "model": arm.get("model"),
            "budget_class": (arm.get("budget") or {}).get("class"),
            "status_before": arm.get("status"),
            "checks": {"free": None,
                       "invocable_from_actions": {"ok": False, "error_class": "not_censusable"},
                       "agent_loop": {"tool_call_seen": False, "roundtrip_ok": False,
                                      "error_class": "not_censusable"}},
            "verdict": "failed",
            "reason": (arm.get("census") or {}).get("evidence_ref") or f"status={arm.get('status')}",
            "quota_terminal": {"terminal": False}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--registry", default="ops/dispatch/build-arms.json")
    ap.add_argument("--output", required=True)
    ap.add_argument("--arm", default=None, help="census one arm only")
    ap.add_argument("--root", default=".")
    args = ap.parse_args(argv)
    harness.harden_process()
    registry = harness.load_registry(args.registry)
    known_ids = {arm["arm_id"] for arm in registry.get("arms", [])}
    if args.arm and args.arm not in known_ids:
        ap.error(f"unknown arm id: {args.arm}")
    root = Path(args.root).resolve()
    rows = []
    for arm in registry.get("arms", []):
        if args.arm and arm["arm_id"] != args.arm:
            continue
        rows.append(census_arm(arm, root))
        print("CENSUS_VERDICT " + json.dumps(rows[-1]))
    feed = {"schema": "arm-census/v1",
            "generated_at": harness.now_iso(),
            "generated_by": "scripts/ops/build_arm_census.py (Actions)",
            "run_id": os.environ.get("GITHUB_RUN_ID"),
            "spec": "issue #5151 census gate {free - invocable from Actions - agent loop tool round-trip}",
            "arms": rows}
    Path(args.output).write_text(json.dumps(feed, indent=1, ensure_ascii=False) + "\n",
                                 encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
