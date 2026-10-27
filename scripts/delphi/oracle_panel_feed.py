#!/usr/bin/env python3
"""Oracle Panel feed collector (oracle-panel-feed/v1).

Builds the dashboard Oracle Panel's data feed from the records of
truth — and nothing else:

  - docs/proposals/registry.yaml        (which proposals exist)
  - docs/proposals/active/<id>/         (generation provenance,
                                         UNVERIFIED points)
  - docs/proposals/passes/<pass-id>/    (pass + cycle records)
  - outcome ledger issue comments       (delphi-generation-ballot /
                                         delphi-generation-calibration
                                         payloads, when fetchable)

Honesty contract (docs/ops/ORACLE-PANEL-FEED.md): the panel must
never show what the record doesn't hold. Ballot classes with no
ballots read as recorded (zero / absent) — never synthesized.
Rehearsals are not registered proposals and never enter the feed;
they are named in `excluded` with their label of record. UNVERIFIED
points and specified_not_run stages are first-class values.

Stdlib only. Auth for the ledger read: GH_TOKEN or GITHUB_TOKEN env,
or --ledger-comments <file> with a pre-fetched comments JSON.
Refresh pattern mirrors scripts/reviewer_metrics/collect.py: the
regenerated feed lands by PR, never by direct commit.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "oracle-panel-feed/v1"
BALLOT_MARKER = "<!-- delphi-generation-ballot v1 -->"
CALIBRATION_MARKER = "<!-- delphi-generation-calibration v1 -->"


def parse_registry(text: str) -> list[dict]:
    """Subset reader for registry.yaml's stable shape.

    Captures each proposal's flat scalar fields; nested blocks
    (reviewers) are skipped by indentation. Fails loudly on an entry
    without an id — a registry the collector can't read must stop
    the feed, not produce a partial one presented as complete.
    """
    proposals: list[dict] = []
    current: dict | None = None
    in_proposals = False
    for line in text.splitlines():
        if re.match(r"^proposals:\s*$", line):
            in_proposals = True
            continue
        if in_proposals and re.match(r"^[a-z_]+:", line):
            break
        if not in_proposals:
            continue
        m = re.match(r"^  - ([a-z_]+):\s*(.*?)\s*$", line)
        if m:
            current = {}
            proposals.append(current)
            if m.group(2):
                current[m.group(1)] = m.group(2).strip("\"'")
            continue
        m = re.match(r"^    ([a-z_]+):\s*(.*?)\s*$", line)
        if m and current is not None:
            key, value = m.group(1), m.group(2)
            if value.startswith("["):
                current[key] = [v.strip() for v in
                                value.strip("[]").split(",") if v.strip()]
            elif value:
                current[key] = value.strip("\"'")
    for entry in proposals:
        if not entry.get("id"):
            raise ValueError("registry entry without an id — refusing to build a partial feed")
    return proposals


def registry_updated_at(text: str) -> str | None:
    m = re.search(r"^updated_at:\s*\"?([^\"\n]+)\"?\s*$", text, re.M)
    return m.group(1).strip() if m else None


def unverified_points(manifest_text: str) -> list[str]:
    points = []
    in_section = False
    for line in manifest_text.splitlines():
        if line.startswith("## "):
            in_section = "Unverified" in line
            continue
        if in_section and line.strip().startswith("- UNVERIFIED:"):
            points.append(line.strip()[2:].removeprefix("UNVERIFIED:").strip())
    return points


def ledger_payloads(comments: list[dict]) -> dict[str, dict]:
    """pass_id -> {ballot: payload, ballot_comment_id, calibration...}"""
    out: dict[str, dict] = {}
    for comment in comments:
        body = comment.get("body") or ""
        for marker, key in ((BALLOT_MARKER, "ballot"),
                            (CALIBRATION_MARKER, "calibration_feed")):
            if marker in body:
                m = re.search(r"```json\s*(\{.*?\})\s*```", body, re.S)
                if not m:
                    continue
                payload = json.loads(m.group(1))
                pass_id = payload.get("pass_id")
                if pass_id:
                    slot = out.setdefault(pass_id, {})
                    slot[key] = payload
                    slot[f"{key}_comment_id"] = comment.get("id")
    return out


def fetch_ledger_comments(repo: str, issue: int, token: str) -> list[dict]:
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/issues/{issue}/comments?per_page=100",
        headers={"Authorization": f"Bearer {token}",
                 "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def build_feed(registry_text: str, active_dir: Path, passes_dir: Path,
               ledger: dict[str, dict], ledger_verified: bool,
               generated_at: str) -> dict:
    entries = parse_registry(registry_text)
    oracle_entries = [e for e in entries if e.get("author") == "oracle-method"]

    passes: dict[str, dict] = {}
    if passes_dir.is_dir():
        for pass_dir in sorted(passes_dir.iterdir()):
            meta_file = pass_dir / "pass.json"
            if not meta_file.exists():
                continue
            meta = json.loads(meta_file.read_text())
            cycle_dir = pass_dir / "cycle"
            cycle = {}
            for name in ("BALLOT-round1.json", "BALLOT-round2.json",
                         "CALIBRATION.json", "CYCLE.json",
                         "EXPECTATIONS.json"):
                f = cycle_dir / name
                if f.exists():
                    cycle[name] = json.loads(f.read_text())
            impl = {}
            impl_dir = pass_dir / "implementation"
            if impl_dir.is_dir():
                for f in impl_dir.glob("*.json"):
                    impl[f.stem] = json.loads(f.read_text())
            passes[meta["pass_id"]] = {"meta": meta, "cycle": cycle,
                                       "impl": impl, "dir": pass_dir}

    proposals = []
    for entry in oracle_entries:
        pid = entry["id"]
        pdir = active_dir / pid
        prov = {}
        if (pdir / "PROVENANCE.json").exists():
            prov = json.loads((pdir / "PROVENANCE.json").read_text())
        unverified = []
        if (pdir / "MANIFEST.md").exists():
            unverified = unverified_points((pdir / "MANIFEST.md").read_text())
        pass_id = prov.get("pass_id")
        item = {
            "id": pid,
            "title": entry.get("title"),
            "author": entry.get("author"),
            "status": entry.get("status"),
            "priority": entry.get("priority"),
            "path": entry.get("path"),
            "pass": pass_id,
            "kind": "pass-candidate" if pass_id else "single",
            "generated_at": prov.get("generated_at"),
            "generator": prov.get("generator"),
            "evidence_items": sum(s.get("items", 0)
                                  for s in prov.get("evidence_sets", [])),
            "unverified_points": unverified,
            "rounds": None,
            "expectations": None,
            "implementation": None,
            "calibration": None,
            "specified_not_run": [],
            "ledger": None,
            "live": True,
        }
        if pass_id and pass_id in passes:
            cyc = passes[pass_id]["cycle"]
            r1 = cyc.get("BALLOT-round1.json") or {}
            r2 = cyc.get("BALLOT-round2.json") or {}
            def scores(ballot: dict) -> dict:
                return {cls: (data.get("scores") or {}).get(pid)
                        for cls, data in (ballot.get("per_class") or {}).items()}
            item["rounds"] = {
                "round_1": {"ranking": r1.get("ranked_outcome"),
                            "rank_of_this": (r1.get("ranked_outcome") or []).index(pid) + 1
                            if pid in (r1.get("ranked_outcome") or []) else None,
                            "ballots_by_class": r1.get("ballots_by_class"),
                            "scores_by_class": scores(r1),
                            "classes_absent": r1.get("classes_absent")},
                "round_2": {"ranking": r2.get("ranked_outcome"),
                            "rank_of_this": (r2.get("ranked_outcome") or []).index(pid) + 1
                            if pid in (r2.get("ranked_outcome") or []) else None,
                            "ballots_by_class": r2.get("ballots_by_class"),
                            "scores_by_class": scores(r2),
                            "evidence_set_sha256": r2.get("evidence_set_sha256")},
            }
            exp_doc = cyc.get("EXPECTATIONS.json") or {}
            priors = exp_doc.get("expectations") or {}
            item["expectations"] = {
                source: per[pid] for source, per in priors.items()
                if isinstance(per, dict) and pid in per} or None
            item["expectations_recorded_before_implementation"] = bool(
                exp_doc.get("recorded_before_implementation"))
            impl = passes[pass_id]["impl"].get(pid)
            if impl:
                suites = impl.get("suites") or []
                item["implementation"] = {
                    "suites": [{"suite": s.get("name"),
                                "passed": s.get("passed"),
                                "failed": s.get("failed")} for s in suites],
                    "passed": sum(s.get("passed") or 0 for s in suites),
                    "failed": sum(s.get("failed") or 0 for s in suites),
                    "suites_total": len(suites),
                    "suites_passed": sum(
                        1 for s in suites
                        if (s.get("failed") or 0) == 0
                        and (s.get("passed") or 0) > 0)}
            cal = (cyc.get("CALIBRATION.json") or {}).get("candidates") or {}
            item["calibration"] = {
                source: {"rank_delta": per[pid]["rank_delta"],
                         "score_delta": per[pid]["score_delta"],
                         "within_tolerance": per[pid]["within_tolerance"],
                         "moved_on_evidence": per[pid]["moved_on_evidence"]}
                for source, per in cal.items() if isinstance(per, dict) and pid in per
            } or None
            stages = (cyc.get("CYCLE.json") or {}).get("stages") or []
            item["specified_not_run"] = [
                {"item": s["stage"], "reason": s.get("detail")}
                for s in stages if s.get("status") == "specified_not_run"]
            led = ledger.get(pass_id) or {}
            ballot = led.get("ballot") or {}
            for name, reason in (ballot.get("specified_not_run") or {}).items():
                item["specified_not_run"].append({"item": name, "reason": reason})
            if led:
                item["ledger"] = {
                    "ballot_comment_id": led.get("ballot_comment_id"),
                    "calibration_comment_id": led.get("calibration_feed_comment_id"),
                    "verified": ledger_verified,
                }
        proposals.append(item)

    pass_summaries = []
    for pass_id, data in passes.items():
        r1 = data["cycle"].get("BALLOT-round1.json") or {}
        pass_summaries.append({
            "pass_id": pass_id,
            "n": data["meta"].get("n"),
            "candidates": [c["id"] for c in data["meta"].get("candidates", [])],
            "ranked_outcome": r1.get("ranked_outcome"),
            "record": f"docs/proposals/passes/{pass_id}/",
        })

    return {
        "schema": SCHEMA,
        "generated_at": generated_at,
        "generator": "scripts/delphi/oracle_panel_feed.py",
        "sources": {
            "registry": "docs/proposals/registry.yaml",
            "registry_updated_at": registry_updated_at(registry_text),
            "registry_proposals_total": len(entries),
            "oracle_method_proposals": len(oracle_entries),
            "ledger_issue": 1487,
            "ledger_verified": ledger_verified,
        },
        "honesty_rules": [
            "Show only what the record holds: a value absent from the "
            "registry, pass records, or ledger payloads is shown as "
            "absent/null, never synthesized.",
            "Ballot classes with no ballots read as recorded "
            "(0 / listed in classes_absent) — never as implied support.",
            "UNVERIFIED points and specified_not_run stages are "
            "first-class statuses: render them, never hide them.",
            "Rehearsals are ideation drafts imagining readiness "
            "(synthetic fixtures, no real ballots, not registered) "
            "and are excluded from results.",
        ],
        "proposals": proposals,
        "passes": pass_summaries,
        "excluded": [{
            "what": "Oracle Method rehearsals on synthetic fixtures",
            "label": "ideation drafts imagining readiness",
            "reason": "not registered proposals; no real ballots; "
                      "never shown as results",
        }],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Oracle Panel feed collector")
    parser.add_argument("--repo", default="timerloggedout-spec/termux-monorepo")
    parser.add_argument("--root", default=".",
                        help="repo checkout root (registry/passes/active read from here)")
    parser.add_argument("--ledger-issue", type=int, default=1487)
    parser.add_argument("--ledger-comments",
                        help="pre-fetched ledger comments JSON (else fetch via GH_TOKEN)")
    parser.add_argument("--no-ledger", action="store_true",
                        help="skip the ledger read (feed marks ledger_verified false)")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    root = Path(args.root)
    registry_text = (root / "docs/proposals/registry.yaml").read_text()

    ledger: dict[str, dict] = {}
    verified = False
    if args.ledger_comments:
        comments = json.loads(Path(args.ledger_comments).read_text())
        ledger = ledger_payloads(comments)
        verified = True
    elif not args.no_ledger:
        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        if token:
            comments = fetch_ledger_comments(args.repo, args.ledger_issue, token)
            ledger = ledger_payloads(comments)
            verified = True
        else:
            print("no token and no --ledger-comments: ledger read skipped",
                  file=sys.stderr)

    feed = build_feed(registry_text,
                      root / "docs/proposals/active",
                      root / "docs/proposals/passes",
                      ledger, verified,
                      datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    Path(args.out).write_text(json.dumps(feed, indent=2) + "\n")
    print(f"oracle-panel-feed: {len(feed['proposals'])} proposals, "
          f"{len(feed['passes'])} passes, ledger_verified={verified}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
