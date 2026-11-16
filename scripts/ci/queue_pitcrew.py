#!/usr/bin/env python3
"""Queue pit crew: diagnose ∧ supersede ∧ suggest (self-improving).

Pass = 1) snapshot queued runs, 2) group by workflow/event, 3) cancel superseded
queued runs of policy-listed idempotent workflows (keep newest per
workflow+event+branch), 4) flag amplifiers (>= threshold queued, not in policy)
as suggestions so the policy grows from evidence. Never touches in_progress.
Policy: ops/queue/pitcrew.json. Kill switch: repo var QUEUE_PITCREW_ENABLED=false.
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.github.com"


def gh(method: str, path: str, token: str):
    req = urllib.request.Request(f"{API}{path}", method=method, headers={
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "termux-monorepo-queue-pitcrew",
        "Authorization": f"Bearer {token}",
    })
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode()
        return json.loads(raw) if raw else {}


def plan(runs: list[dict], policy: dict) -> dict:
    """Pure decision step (unit-tested): what to cancel ∧ what to suggest."""
    supersede = set(policy.get("supersede", []))
    by_wf = collections.Counter(r.get("name") or "?" for r in runs)
    by_event = collections.Counter(r.get("event") or "?" for r in runs)
    groups: dict[tuple, list[dict]] = collections.defaultdict(list)
    for r in runs:
        if r.get("status") != "queued":
            continue
        if (r.get("name") or "") in supersede:
            groups[(r.get("name"), r.get("event"), r.get("head_branch"))].append(r)
    cancel: list[int] = []
    for members in groups.values():
        members.sort(key=lambda r: (r.get("created_at") or "", r.get("id") or 0))
        cancel += [m["id"] for m in members[:-1]]
    cancel = cancel[: int(policy.get("max_cancels_per_pass", 400))]
    thr = int(policy.get("amplifier_threshold", 50))
    suggest = [w for w, n in by_wf.most_common() if n >= thr and w not in supersede]
    return {
        "queued": len(runs),
        "by_workflow": by_wf.most_common(15),
        "by_event": by_event.most_common(),
        "cancel": cancel,
        "suggest_supersede": suggest,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True)
    p.add_argument("--policy", default="ops/queue/pitcrew.json")
    p.add_argument("--max-pages", type=int, default=20)
    p.add_argument("--apply", action="store_true")
    a = p.parse_args()
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GH_TOKEN required", file=sys.stderr)
        return 2
    policy = json.load(open(a.policy))
    runs: list[dict] = []
    for page in range(1, a.max_pages + 1):
        q = urllib.parse.urlencode({"status": "queued", "per_page": 100, "page": page})
        batch = gh("GET", f"/repos/{a.repo}/actions/runs?{q}", token).get("workflow_runs") or []
        runs += batch
        if len(batch) < 100:
            break
    decision = plan(runs, policy)
    done = failed = 0
    for rid in decision["cancel"]:
        if not a.apply:
            continue
        try:
            gh("POST", f"/repos/{a.repo}/actions/runs/{rid}/cancel", token)
            done += 1
        except urllib.error.HTTPError:
            failed += 1
    out = {**decision, "cancel": len(decision["cancel"]), "cancelled": done,
           "cancel_failed": failed, "apply": a.apply}
    print(json.dumps(out))
    for w in decision["suggest_supersede"]:
        print(f"::notice title=pitcrew suggest::{w} has >= {policy.get('amplifier_threshold')} queued; review for supersede/coalesce")
    summ = os.environ.get("GITHUB_STEP_SUMMARY")
    if summ:
        with open(summ, "a") as f:
            f.write("## Queue pit crew\n```json\n" + json.dumps(out, indent=1) + "\n```\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
