#!/usr/bin/env python3
"""3L0 discrimination watch — the diagnostic trigger for the 3L0 plane.

Reads the collected 3L0 feed (`apps/help-wanted-dashboard/data/3l0-feed.json`).
While the observed Delphi weights' `discrimination.effective_weight_driver`
is `seed_base_only` (the observed factors are identical across roles, so the
effective weights reproduce only the seed base ratios), this watch keeps
exactly ONE open diagnostic issue:

- no open watch issue            -> open one (action: open)
- open issue, same fingerprint   -> no-op (action: noop)
- open issue, new fingerprint    -> comment the new state (action: update)
- driver no longer seed_base_only and an issue is open
                                 -> comment + close (action: resolve)
- driver no longer seed_base_only, none open -> no-op

The fingerprint is sha256 over the canonical discrimination block plus the
observed provenance (newest ledger comment id), so a re-run over unchanged
state never spams, and any change in the underlying observation re-fires.

The upgrade the diagnostic points at is issue #1784 (Delphi weighting v2:
per-role{moniker} equivalence-class Elo, per-voter EWMA, idempotent
feedback). This script never edits weights, feeds, or ledgers.

GitHub access is via the `gh` CLI (GH_TOKEN in the collect workflow).
API failures degrade to a ::warning:: and exit 0 — the watch never fails
the feed collect. `--dry-run` prints the decision as JSON and performs
the issue lookup read-only (no writes).
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

MARKER = "<!-- 3l0-discrimination-watch v1"
TITLE = "[3L0] discrimination watch: effective weights are seed_base_only"
UPGRADE_ISSUE = 1784
FEED = Path("apps/help-wanted-dashboard/data/3l0-feed.json")


def extract(feed: dict) -> dict:
    data = feed.get("data") or {}
    weights = data.get("delphi_weights") or {}
    observed = weights.get("observed") or {}
    disc = observed.get("discrimination") or {}
    prov = observed.get("provenance") or {}
    return {
        "driver": disc.get("effective_weight_driver"),
        "discrimination": disc,
        "newest_comment_id": prov.get("newest_comment_id"),
        "observed_at": observed.get("observed_at"),
        "read_at": observed.get("read_at"),
    }


def fingerprint(state: dict) -> str:
    canon = json.dumps(
        {"discrimination": state.get("discrimination"),
         "newest_comment_id": state.get("newest_comment_id")},
        sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canon.encode()).hexdigest()[:16]


def decide(driver, open_issue: bool, existing_fp, current_fp: str) -> str:
    """Pure decision: one of open / update / noop / resolve."""
    if driver == "seed_base_only":
        if not open_issue:
            return "open"
        return "noop" if existing_fp == current_fp else "update"
    return "resolve" if open_issue else "noop"


def marker_line(fp: str) -> str:
    return f"{MARKER} fingerprint:{fp} -->"


def render_body(state: dict, fp: str, action: str) -> str:
    disc = state.get("discrimination") or {}
    return (
        f"{marker_line(fp)}\n\n"
        f"[MUSEai]@{{role:{{3l0-plane}}}} discrimination watch ({action}).\n\n"
        f"The collected 3L0 feed reports `effective_weight_driver = "
        f"seed_base_only`: the observed Delphi weights carry no "
        f"differentiating signal, so effective weights reproduce only the "
        f"seed base ratios.\n\n"
        f"- uniform_fields: `{json.dumps(disc.get('uniform_fields'))}`\n"
        f"- appends: {disc.get('appends')} over "
        f"{disc.get('distinct_outcome_events')} distinct outcome event(s): "
        f"`{json.dumps(disc.get('outcome_events'))}`\n"
        f"- observed_at: {state.get('observed_at')} "
        f"(ledger comment {state.get('newest_comment_id')})\n"
        f"- fingerprint: `{fp}`\n\n"
        f"Note on record: {disc.get('note', '')}\n\n"
        f"Upgrade of record: #{UPGRADE_ISSUE} (Delphi weighting v2 — "
        f"per-role{{moniker}} equivalence-class Elo, per-voter EWMA, "
        f"idempotent feedback). This issue is the standing diagnostic; it "
        f"updates only when the fingerprint changes and closes itself "
        f"when the driver is no longer `seed_base_only`."
    )


def gh(*args, check=True):
    out = subprocess.run(["gh", *args], capture_output=True, text=True)
    if check and out.returncode != 0:
        raise RuntimeError(out.stderr.strip()[:300])
    return out


def find_open_issue() -> dict | None:
    """Return {number, body_fingerprint} for the open watch issue, or None."""
    out = gh("issue", "list", "--state", "open", "--search",
             f'"{TITLE}" in:title', "--json", "number,body", "--limit", "5")
    issues = json.loads(out.stdout or "[]")
    for issue in issues:
        body = issue.get("body") or ""
        fp = None
        for line in body.splitlines():
            if line.startswith(MARKER) and "fingerprint:" in line:
                fp = line.split("fingerprint:")[1].split()[0].rstrip(">").strip()
        return {"number": issue["number"], "fingerprint": fp}
    return None


def comment_fingerprints(number: int) -> set:
    out = gh("issue", "view", str(number), "--json", "comments")
    fps = set()
    for comment in (json.loads(out.stdout or "{}").get("comments") or []):
        for line in (comment.get("body") or "").splitlines():
            if line.startswith(MARKER) and "fingerprint:" in line:
                fps.add(line.split("fingerprint:")[1].split()[0].rstrip(">").strip())
    return fps


def main(argv) -> int:
    dry_run = "--dry-run" in argv
    feed_path = FEED
    if "--feed" in argv:
        feed_path = Path(argv[argv.index("--feed") + 1])
    state = extract(json.loads(feed_path.read_text()))
    fp = fingerprint(state)
    try:
        existing = find_open_issue()
    except Exception as exc:  # degrade, never fail the collect
        print(f"::warning::discrimination watch lookup failed: {exc}")
        print(json.dumps({"action": "deferred", "fingerprint": fp}))
        return 0
    seen_fps = set()
    if existing:
        if existing["fingerprint"]:
            seen_fps.add(existing["fingerprint"])
        seen_fps |= comment_fingerprints(existing["number"])
    action = decide(state["driver"], bool(existing),
                    fp if fp in seen_fps else None, fp)
    print(json.dumps({"action": action, "fingerprint": fp,
                      "driver": state["driver"],
                      "issue": existing["number"] if existing else None}))
    if dry_run or action == "noop":
        return 0
    body = render_body(state, fp, action)
    try:
        if action == "open":
            gh("issue", "create", "--title", TITLE, "--body", body)
        elif action == "update":
            gh("issue", "comment", str(existing["number"]), "--body", body)
        elif action == "resolve":
            gh("issue", "comment", str(existing["number"]), "--body",
               f"{marker_line(fp)}\n\n[MUSEai]@{{role:{{3l0-plane}}}} "
               f"Resolved: the collected 3L0 feed no longer reports "
               f"`seed_base_only` (driver: `{state['driver']}`). Closing "
               f"the standing diagnostic.")
            gh("issue", "close", str(existing["number"]))
    except Exception as exc:
        print(f"::warning::discrimination watch write failed: {exc}")
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
