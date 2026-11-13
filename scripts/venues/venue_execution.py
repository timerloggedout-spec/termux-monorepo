#!/usr/bin/env python3
"""Venue-execution machinery (QUE #5254).

Executes the fleet-executable class of an entry's submission-
requirements census (entries/<slug>/submission-requirements.json)
in repo machinery — never a seat-browser leg:

    execute (per-venue adapter) -> unauthenticated verify of the
    public artifact -> receipt stamp on the entry's filing.

SUBMIT-ONCE is enforced here, not by convention: state is keyed
{slug}/{venue}/{requirement}; a requirement whose key already
carries a verified execution is READ, never re-sent (a second fire
re-verifies the recorded public URL and reports the existing
state). Venue refusal / closed state surfaces as a named receipt —
fail-visible, never a silent fallback.

Credentials: fleet venue accounts via sealed secrets ONLY, by name
of record (bindings name the env var; values never enter the repo).

Usage:
  python3 scripts/venues/venue_execution.py execute \
      --entry d1-studysprint --requirement demo-video-upload \
      [--artifact path/to/media] [--state ops/venue-execution/state.json] \
      [--dry-run] [--now ISO] [--run-id ID]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import clips_adapter  # noqa: E402
import webform_adapter  # noqa: E402

ADAPTERS = {"clips": clips_adapter, "webform": webform_adapter}
STATE_SCHEMA = "venue-execution-state/v1"
EXECUTABLE_CLASS = "fleet-executable"


def now_iso(now: datetime | None = None) -> str:
    return (now or datetime.now(timezone.utc)).isoformat().replace(
        "+00:00", "Z")


def load_json(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_state(path: Path) -> dict:
    if Path(path).exists():
        return load_json(path)
    return {"schema": STATE_SCHEMA, "executions": {}}


def save_state(path: Path, state: dict) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(state, indent=1, sort_keys=True) + "\n",
                          encoding="utf-8")


def verify_public(url: str, expect_contains: str | None = None,
                  opener=None) -> dict:
    """Unauthenticated verification read: a brand-new opener, NO
    credential headers of any kind (the no-login check is the
    evidence — a seat's authenticated fetch proves nothing)."""
    req = urllib.request.Request(url, method="GET")
    # No CREDENTIAL headers — that is the no-login invariant. A
    # descriptive User-Agent is still sent: several public hosts
    # 403 library-default agents (tmpfiles dl path, run 43366207635),
    # which would masquerade as a login wall.
    req.add_header("User-Agent",
                   "termux-fleet/venue-execution-verify "
                   "(+https://github.com/timerloggedout-spec/termux-monorepo)")
    assert "Authorization" not in req.headers
    assert "Cookie" not in req.headers
    open_fn = opener or urllib.request.urlopen
    try:
        with open_fn(req, timeout=30) as resp:
            body = resp.read(65536)
            status = resp.status
    except Exception as exc:
        return {"ok": False, "status": None, "bytes": 0,
                "error": f"{type(exc).__name__}: {exc}"[:200]}
    ok = status == 200
    if expect_contains:
        ok = ok and expect_contains.encode() in body
    return {"ok": ok, "status": status, "bytes": len(body),
            "contains_expected": (expect_contains in body.decode(
                "utf-8", "replace")) if expect_contains else None}


def plan_execution(census: dict, bindings: dict, requirement_id: str) -> dict:
    """Gate one requirement for execution. Returns a plan dict with
    action execute|skip and the reason — class gating lives here:
    only fleet-executable, non-discharged requirements with a
    binding may execute."""
    req = next((r for r in census.get("requirements", [])
                if r.get("id") == requirement_id), None)
    if req is None:
        return {"action": "skip", "reason": "requirement_not_in_census"}
    if req.get("class") != EXECUTABLE_CLASS:
        return {"action": "skip",
                "reason": f"class_not_fleet_executable:{req.get('class')}"}
    if req.get("discharged"):
        return {"action": "skip", "reason": "already_discharged"}
    binding = (bindings.get("bindings") or {}).get(requirement_id)
    if binding is None:
        return {"action": "skip", "reason": "no_venue_binding"}
    if binding.get("adapter") not in ADAPTERS:
        return {"action": "skip",
                "reason": f"unknown_adapter:{binding.get('adapter')}"}
    return {"action": "execute", "requirement": req, "binding": binding}


def execute(entry_slug: str, requirement_id: str, artifact: str | None,
            root: Path, state_path: Path, dry_run: bool = False,
            now: datetime | None = None, run_id: str = "local",
            transport=None) -> dict:
    """One machinery execution (or SUBMIT-ONCE read-back). Pure of
    network except through the adapter + verify legs."""
    census = load_json(root / "entries" / entry_slug
                       / "submission-requirements.json")
    bindings = load_json(root / "entries" / entry_slug
                         / "venue-execution.json")
    plan = plan_execution(census, bindings, requirement_id)
    stamp = now_iso(now)
    if plan["action"] == "skip":
        return {"schema": "venue-execution-receipt/v1", "entry": entry_slug,
                "requirement": requirement_id, "outcome": "skipped",
                "reason": plan["reason"], "at": stamp, "run_id": run_id}
    binding = plan["binding"]
    venue = binding.get("venue", binding["adapter"])
    key = f"{entry_slug}/{venue}/{requirement_id}"
    state = load_state(state_path)
    prior = (state.get("executions") or {}).get(key)
    submit_once = bool(plan["requirement"].get("submit_once")) \
        or bool(binding.get("submit_once", True))
    if prior and prior.get("verified") and submit_once:
        # SUBMIT-ONCE: read state, re-verify the recorded URL, never
        # re-send. The adapter is not invoked on this path.
        verify = verify_public(prior["public_url"],
                               binding.get("verify_contains"))
        return {"schema": "venue-execution-receipt/v1", "entry": entry_slug,
                "requirement": requirement_id, "outcome": "already_executed",
                "venue": venue, "public_url": prior["public_url"],
                "verify": verify, "first_executed_at": prior.get("at"),
                "at": stamp, "run_id": run_id}
    adapter = ADAPTERS[binding["adapter"]]
    result = adapter.execute(binding, artifact, transport=transport)
    if result.get("status") != "executed":
        return {"schema": "venue-execution-receipt/v1", "entry": entry_slug,
                "requirement": requirement_id, "outcome": "venue_refused",
                "venue": venue, "reason": result.get("reason"),
                "detail": result.get("detail"), "at": stamp,
                "run_id": run_id}
    verify = verify_public(result["public_url"],
                           binding.get("verify_contains"))
    record = {"venue": venue, "public_url": result["public_url"],
              "verified": bool(verify["ok"]), "verify": verify,
              "at": stamp, "run_id": run_id,
              "adapter": binding["adapter"]}
    if not dry_run:
        state.setdefault("executions", {})[key] = record
        save_state(state_path, state)
    return {"schema": "venue-execution-receipt/v1", "entry": entry_slug,
            "requirement": requirement_id,
            "outcome": "executed" if verify["ok"] else "executed_unverified",
            "venue": venue, "public_url": result["public_url"],
            "verify": verify, "at": stamp, "run_id": run_id,
            "dry_run": dry_run}


def receipt_comment(receipt: dict) -> str:
    lines = [
        f"[MUSEai]@{{role:{{venue-execution}}}} VENUE EXECUTION — "
        f"{receipt['entry']} / {receipt['requirement']}: "
        f"**{receipt['outcome']}**",
        "",
        f"- venue: {receipt.get('venue')}",
        f"- public URL: {receipt.get('public_url')}",
        f"- run: {receipt.get('run_id')} at {receipt.get('at')}",
    ]
    verify = receipt.get("verify") or {}
    if verify:
        lines.append(
            f"- unauthenticated verify: ok={verify.get('ok')} "
            f"status={verify.get('status')} bytes={verify.get('bytes')}")
    if receipt.get("reason"):
        lines.append(f"- reason: {receipt['reason']}")
    if receipt["outcome"] == "already_executed":
        lines.append("- SUBMIT-ONCE: prior verified execution read "
                     "from state; nothing re-sent.")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)
    ex = sub.add_parser("execute")
    ex.add_argument("--entry", required=True)
    ex.add_argument("--requirement", required=True)
    ex.add_argument("--artifact")
    ex.add_argument("--root", default=".")
    ex.add_argument("--state", default="ops/venue-execution/state.json")
    ex.add_argument("--dry-run", action="store_true")
    ex.add_argument("--now")
    ex.add_argument("--run-id", default=os.environ.get("GITHUB_RUN_ID",
                                                       "local"))
    ex.add_argument("--receipt-out")
    args = ap.parse_args(argv)
    now = None
    if args.now:
        now = datetime.fromisoformat(args.now.replace("Z", "+00:00"))
    receipt = execute(args.entry, args.requirement, args.artifact,
                      Path(args.root), Path(args.state),
                      dry_run=args.dry_run, now=now, run_id=args.run_id)
    text = json.dumps(receipt, indent=1, sort_keys=True)
    if args.receipt_out:
        Path(args.receipt_out).write_text(text + "\n", encoding="utf-8")
    print(text)
    print("\n" + receipt_comment(receipt))
    return 0 if receipt["outcome"] in ("executed", "already_executed",
                                        "skipped") else 1


if __name__ == "__main__":
    raise SystemExit(main())
