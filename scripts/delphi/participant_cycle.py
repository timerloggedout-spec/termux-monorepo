#!/usr/bin/env python3
"""Delphi participant cycle — the scheduled check for research participants.

Owner order 2026-10-28 reclassified the 48 research-silo filings from gate
applicants to Delphi process participants (docs/ops/RESEARCH-SILO-DELPHI.md
§4c, registry ops/delphi/research-participants.json). The gate sweeps by the
delphi:rfp label, so participants need their own scheduled check — this is
it. It enumerates the participant REGISTRY (not labels), and for each
participant whose axes cycle is due, posts a cycle record:

  * one `<!-- delphi-participant-cycle v1 -->` comment on the participant's
    baseline issue, carrying the silo's current axes states (from
    ops/delphi/research-axes.json) as a JSON block, and
  * one summary record on the outcome ledger (exact-title resolution) when
    at least one participant was processed.

Cycle cadence = panel.json award.research_recheck_days (2 days). A
participant is due when it has no cycle record yet, or its newest record's
next_due has passed. Records are append-only; nothing is edited or scored —
participants are not gate applicants and this job never touches the gate.

Rate discipline mirrors the gate's defer_api: when the token's core
remaining is under the reserve, the run defers (exit 0, nothing posted).

Stdlib only. Env: GH_TOKEN (or GITHUB_TOKEN), GH_REPO=owner/repo.
Flags: --dry-run (plan only, no writes).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

MARK = "<!-- delphi-participant-cycle v1 -->"
OUTCOMES_TITLE = "Delphi outcome ledger"
RATE_RESERVE = 150
AXES = ("produced_output_results_validated", "feature_extractions",
        "consensus_implementation")
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")


def now_dt() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


class GH:
    def __init__(self, token: str, repo: str):
        self.base = f"https://api.github.com/repos/{repo}"
        self.token = token

    def req(self, method: str, path: str, body: dict | None = None):
        data = json.dumps(body).encode() if body is not None else None
        r = urllib.request.Request(
            self.base + path, data=data, method=method,
            headers={"Authorization": f"Bearer {self.token}",
                     "Accept": "application/vnd.github+json",
                     "Content-Type": "application/json",
                     "User-Agent": "delphi-participant-cycle"})
        with urllib.request.urlopen(r) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else {}

    def rate_remaining(self) -> int:
        r = urllib.request.Request(
            "https://api.github.com/rate_limit",
            headers={"Authorization": f"Bearer {self.token}",
                     "Accept": "application/vnd.github+json",
                     "User-Agent": "delphi-participant-cycle"})
        with urllib.request.urlopen(r) as resp:
            return json.loads(resp.read().decode())["resources"]["core"]["remaining"]

    def comments(self, number: int) -> list[dict]:
        out, page = [], 1
        while True:
            batch = self.req("GET", f"/issues/{number}/comments?per_page=100&page={page}")
            if not batch:
                return out
            out += batch
            page += 1

    def find_issue_by_title(self, title: str, label: str) -> int | None:
        found = self.req("GET", f"/issues?state=open&labels={label}&per_page=20")
        for i in found:
            if i.get("title") == title:
                return i["number"]
        return None


def load(rel: str):
    with open(os.path.join(ROOT, rel)) as f:
        return json.load(f)


def newest_record(comments: list[dict]) -> dict | None:
    rec = None
    for c in comments:
        body = c.get("body", "")
        if body.startswith(MARK) and "```json" in body:
            try:
                rec = json.loads(body.split("```json", 1)[1].split("```", 1)[0])
            except Exception:
                continue
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GH_REPO") or os.environ.get("GITHUB_REPOSITORY")
    if not token or not repo:
        print("GH_TOKEN/GH_REPO missing", file=sys.stderr)
        return 2
    gh = GH(token, repo)

    if gh.rate_remaining() < RATE_RESERVE:
        print("defer: rate remaining under reserve; nothing posted")
        return 0

    registry = load("ops/delphi/research-participants.json")
    axes_doc = load("ops/delphi/research-axes.json")
    panel = load("ops/delphi/panel.json")
    recheck_days = int(panel.get("award", {}).get("research_recheck_days", 2))
    silos_axes = axes_doc.get("silos", {})
    now = now_dt()
    processed: list[dict] = []

    for p in registry.get("participants", []):
        silo = p["silo_id"]
        baseline = int(p["filings"]["baseline"])
        prev = newest_record(gh.comments(baseline))
        if prev is not None:
            due_at = datetime.strptime(prev["next_due"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            if now < due_at:
                continue
            cycle = int(prev["cycle"]) + 1
        else:
            cycle = int(axes_doc.get("cycle", 1))
        entry = silos_axes.get(silo, {})
        record = {
            "participant": silo,
            "cycle": cycle,
            "recorded_at": iso(now),
            "axes": {a: (entry.get(a, {}) or {}).get("state", "unrecorded") for a in AXES},
            "arms": p["filings"],
            "next_due": iso(now + timedelta(days=recheck_days)),
            "source": "delphi-participant-cycle (scheduled; registry-enumerated)",
        }
        body = (f"{MARK}\n### Delphi participant cycle {cycle}: `{silo}`\n\n"
                f"Participant axes record (post-hoc, never a gate score). "
                f"Next cycle due {record['next_due']}.\n\n"
                f"```json\n{json.dumps(record, indent=1)}\n```")
        if args.dry_run:
            print(f"DRY-RUN would post cycle {cycle} record on #{baseline} ({silo})")
        else:
            gh.req("POST", f"/issues/{baseline}/comments", {"body": body})
            print(f"posted cycle {cycle} record on #{baseline} ({silo})")
        processed.append(record)

    if processed and not args.dry_run:
        ledger = gh.find_issue_by_title(OUTCOMES_TITLE, "delphi:outcomes")
        if ledger is not None:
            lines = ", ".join(f"`{r['participant']}` cycle {r['cycle']}" for r in processed)
            gh.req("POST", f"/issues/{ledger}/comments", {"body":
                f"{MARK}\nParticipant cycle sweep ({iso(now)}): {len(processed)} participant(s) processed — {lines}. "
                f"Records on each participant's baseline issue; axes states from ops/delphi/research-axes.json."})
            print(f"summary posted on #{ledger}")
    print(f"done: {len(processed)} participant(s) due/processed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
