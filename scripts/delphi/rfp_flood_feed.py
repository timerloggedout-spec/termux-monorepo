#!/usr/bin/env python3
"""Delphi RFP flood feed collector — schema delphi-rfp-feed/v1.

Reads a cache directory (issues.json + comments.json in GitHub API
shape, surfaces.json + panel.json from ops/delphi/) and emits the
feed the dashboard renders: every open delphi:rfp issue with its
status, the criteria it is judged under, the form questions with the
responses as filed, the gate outcome, and the panel's signed votes
(the responses) verbatim from the gate ledger comment.

Honesty rules (contract: docs/ops/DELPHI-RFP-FEED.md): an RFP with no
gate ledger comment is `unscored` with the gap named — never inferred;
votes are carried verbatim, never paraphrased into new scores;
research-silo comparison axes are post-hoc records, not gate scores.

Usage: rfp_flood_feed.py --cache DIR --out FEED.json
The cache is produced by rfp_flood_fetch.py (Actions) or any
authenticated GitHub client.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "delphi-rfp-feed/v1"
LEDGER_MARK = "<!-- delphi-ledger v1 -->"

# The questions every RFP answers — .github/ISSUE_TEMPLATE/delphi-rfp.yml
# (field id -> the form's label). Responses are parsed from the filed
# issue body under the matching ### heading.
QUESTIONS = [
    ("surface_id", "Surface id"),
    ("lane", "Lane"),
    ("filed_by_collaboration_lane", "Filed by (collaboration lane)"),
    ("gantt_plan", "Gantt plan"),
    ("free_quota", "Free quota"),
    ("reset_and_zone", "Reset and zone"),
    ("auth_from_actions", "Auth from Actions"),
    ("lock_in", "Lock-in"),
    ("failure_modes", "Failure modes"),
    ("evidence_links", "Evidence links"),
]

STATUS_LABELS = ("shadow", "promoted", "parked")  # award labels only; converged is a rounds property
RESEARCH_AXES = ["produced_output_results_validated",
                 "feature_extractions", "consensus_implementation"]


def parse_form(body: str) -> dict:
    """Same heading parser the gate uses (gate.py parse_form)."""
    out, key = {}, None
    for line in (body or "").splitlines():
        m = re.match(r"^###\s+(.+?)\s*$", line)
        if m:
            key = re.sub(r"[^a-z0-9]+", "_", m.group(1).lower()).strip("_")
            out[key] = ""
        elif key is not None:
            out[key] = (out[key] + "\n" + line).strip()
    return {k: ("" if v == "_No response_" else v) for k, v in out.items()}


def surface_id(issue: dict, form: dict) -> str | None:
    sid = (form.get("surface_id") or "").strip()
    if sid:
        return sid
    m = re.search(r"\[delphi:rfp\]\s*([a-z0-9._-]+)", issue.get("title", ""))
    return m.group(1) if m else None


def classify(sid: str | None, catalog: dict) -> tuple[str, str | None, str | None]:
    """(group, silo_slot, variant) for a surface id."""
    if sid and sid.startswith("research."):
        rest = sid[len("research."):]
        for variant in ("rnd", "selected", "control"):
            if rest.endswith("." + variant):
                return "research-variant", rest[: -len(variant) - 1], variant
        return "research-baseline", rest, None
    if sid and sid in catalog:
        return "surface", None, None
    return "synthetic", None, None


def parse_ledger(comment: dict) -> dict:
    body = comment["body"]
    out: dict = {"comment_id": comment["id"], "created_at": comment["created_at"]}
    m = re.search(r"\*\*Award:\*\*\s*(.+)", body)
    if m:
        out["award_line"] = m.group(1).strip()
    m = re.search(r"\*\*effective_score\*\*\s*([\d.]+) / 25 · converged (\w+) after (\d+)", body)
    if m:
        out["effective_score"] = float(m.group(1))
        out["converged"] = m.group(2) == "True"
        out["rounds_count"] = int(m.group(3))
    m = re.search(r"trigger `([^`]+)`", body)
    if m:
        out["trigger"] = m.group(1)
    rounds = []
    for row in re.finditer(r"\| (\d+) \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \|", body):
        rounds.append({"round": int(row.group(1)), "median": float(row.group(2)),
                       "iqr": float(row.group(3)), "effective": float(row.group(4))})
    if rounds:
        out["rounds"] = rounds
    m = re.search(r"^Oracle: (.+)$", body, re.M)
    if m:
        out["oracle"] = m.group(1).strip()
    m = re.search(r"```json\n(.*?)\n```", body, re.S)
    if m:
        try:
            payload = json.loads(m.group(1))
        except json.JSONDecodeError:
            payload = {}
        out["input_hash"] = payload.get("input_hash")
        if payload.get("award"):
            out["award"] = payload["award"]
        votes = []
        for v in payload.get("final_votes", []):
            votes.append({k: v.get(k) for k in
                          ("role", "score", "impact", "importance", "veto",
                           "reason", "via", "signed")})
        if votes:
            out["votes"] = votes
        if payload.get("records"):
            out["records"] = payload["records"]
    return out


def build(cache: Path, generated_at: str) -> dict:
    missing = [n for n in ("issues.json", "comments.json", "surfaces.json", "panel.json")
               if not (cache / n).exists()]
    if missing:
        raise ValueError(f"refusing a partial feed: cache is missing {missing}")
    issues = json.loads((cache / "issues.json").read_text())
    comments = json.loads((cache / "comments.json").read_text())
    surfaces = json.loads((cache / "surfaces.json").read_text())
    panel = json.loads((cache / "panel.json").read_text())
    catalog = {s["id"]: s for s in surfaces.get("surfaces", [])}

    rfps = []
    for issue in sorted(issues, key=lambda i: i["number"]):
        form = parse_form(issue.get("body") or "")
        sid = surface_id(issue, form)
        group, silo, variant = classify(sid, catalog)
        labels = [l["name"] for l in issue.get("labels", [])]
        status = next((s for s in STATUS_LABELS if f"delphi:{s}" in labels), None)
        gaps = []
        questions = []
        for field, label in QUESTIONS:
            response = form.get(field) or None
            if response is None:
                gaps.append(f"form field '{field}' absent from the filing")
            questions.append({"field": field, "question": label, "response": response})
        ledger_comments = [c for c in comments.get(str(issue["number"]), [])
                           if c["body"].startswith(LEDGER_MARK)]
        outcome = responses = None
        converged_flag = "delphi:converged" in labels
        if ledger_comments:
            parsed = parse_ledger(ledger_comments[-1])
            outcome = {k: parsed.get(k) for k in
                       ("award_line", "award", "effective_score", "converged",
                        "rounds_count", "rounds", "trigger", "input_hash",
                        "comment_id", "created_at")
                       if parsed.get(k) is not None}
            responses = {}
            if parsed.get("votes"):
                responses["votes"] = parsed["votes"]
            if parsed.get("oracle"):
                responses["oracle"] = parsed["oracle"]
            if parsed.get("records"):
                responses["records"] = parsed["records"]
            if not responses:
                responses = None
                gaps.append("gate ledger comment carries no signed votes block")
        else:
            gaps.append("no gate ledger comment yet — the gate has not scored this filing on record")
        # Status is the gate's AWARD (latest ledger decision) when one
        # exists: 'converged' is a rounds property, not an award — 18
        # parked RFPs also carry the converged label (verified in the
        # 2026-10-27 census). Label precedence applies only pre-award.
        if outcome and outcome.get("award", {}).get("decision"):
            status = outcome["award"]["decision"]
        elif status is None:
            status = "unscored"
            gaps.append("no delphi: status label (shadow/promoted/parked/converged) applied")
        votes_cast = len(responses["votes"]) if responses and "votes" in responses else 0
        entry = {
            "number": issue["number"],
            "progress": {
                "stage": "gate-scored" if outcome else "awaiting-gate",
                "rounds_run": (outcome or {}).get("rounds_count", 0),
                "rounds_max": 3,
                "votes_cast": votes_cast,
                "votes_expected": len(panel.get("roles", {})) or 5,
            },
            "title": issue["title"],
            "url": issue["html_url"],
            "created_at": issue["created_at"],
            "surface_id": sid,
            "lane": form.get("lane") or None,
            "group": group,
            "status": status,
            "converged": bool(converged_flag or (outcome or {}).get("converged")),
            "labels": labels,
            "scoring_inputs": ("sourced surface (ops/delphi/surfaces.json)"
                               if group == "surface" else
                               "synthetic unsourced surface — rubric scores from the form only "
                               "(fit 3, headroom 3, horizon H2)"),
            "questions": questions,
            "outcome": outcome,
            "responses": responses,
            "gaps": gaps,
        }
        if silo:
            entry["silo"] = silo
        if variant:
            entry["variant"] = variant
        if group.startswith("research"):
            entry["comparison_axes"] = {axis: "pending — recorded post-hoc per "
                                              "RESEARCH-SILO-DELPHI.md, not gate-scored"
                                        for axis in RESEARCH_AXES}
        rfps.append(entry)

    baselines = {r["silo"]: r["number"] for r in rfps if r["group"] == "research-baseline"}
    for r in rfps:
        if r["group"] == "research-variant":
            r["parent"] = {"number": baselines.get(r["silo"]),
                           "surface_id": f"research.{r['silo']}"}
    by_status: dict[str, int] = {}
    by_group: dict[str, int] = {}
    for r in rfps:
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1
        by_group[r["group"]] = by_group.get(r["group"], 0) + 1
    roles = panel.get("roles", {})
    return {
        "schema": SCHEMA,
        "generated_at": generated_at,
        "source": "open GitHub issues labeled delphi:rfp + their gate ledger comments (live census at generation)",
        "summary": {"total_open": len(rfps), "by_status": by_status, "by_group": by_group},
        "criteria": {
            "scale": "effective_score / 25, from up to 3 panel rounds (median/IQR convergence)",
            "shadow_bar": 15.0,
            "award_bands": "shadow at/above the bar; parked below it with a recheck; promoted/converged per the gate ledger labels",
            "roles": {name: {"base_weight_role": cfg.get("role", name)}
                      for name, cfg in roles.items()} if roles else {},
            "roles_note": "5-role blind panel (OPERATOR, builder, reviewer, Scout, cost_auditor); live weights are the #1489 ledger's, panel.json carries cold-start defaults",
            "money_veto": "cost_auditor vetoes surfaces whose filing requires a payment instrument or auto-bills overages (score capped at 4)",
            "questions_source": ".github/ISSUE_TEMPLATE/delphi-rfp.yml — the 10 form questions every RFP answers; per-RFP responses are in each entry's questions[]",
            "research_axes_note": "research.* RFPs: the gate score is an admission rubric only (synthetic surfaces); the comparison axes (produced outputs validated / feature extractions / consensus implementation) are post-hoc records, shown per RFP as comparison_axes",
            "items": [
                {"id": "scale", "text": "effective_score / 25 decides the award"},
                {"id": "rounds", "text": "up to 3 blind panel rounds; rounds report median + IQR until convergence"},
                {"id": "shadow_bar", "text": "shadow award at effective_score >= 15.0; below it the RFP parks with a recheck date"},
                {"id": "roles", "text": "5-role blind panel: OPERATOR, builder, reviewer, Scout, cost_auditor; live weights are the #1489 ledger's"},
                {"id": "money_veto", "text": "cost_auditor vetoes filings requiring a payment instrument or auto-billing overages (score capped at 4)"},
                {"id": "research_axes", "text": "research.* RFPs only: validated outputs / feature extractions / consensus implementation are the real criteria, recorded post-hoc — the gate score is admission only"},
            ],
        },
        "honesty_rules": [
            "Status comes from the gate's labels and its latest ledger comment; an RFP with neither is 'unscored' with the gap named — never inferred.",
            "Responses are the panel's signed votes verbatim from the ledger comment (role, score, reason, sign-off); nothing is paraphrased into a new score.",
            "A form field absent from a filing is an explicit gap entry, not an empty string.",
            "Research-silo comparison axes read 'pending' until a post-hoc record exists — never zero, never a gate score.",
            "Counts in summary are derived from the entries in this file at generation time.",
        ],
        "rfps": rfps,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cache", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    feed = build(Path(args.cache),
                 datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    Path(args.out).write_text(json.dumps(feed, indent=1) + "\n")
    print(f"wrote {args.out}: {feed['summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
