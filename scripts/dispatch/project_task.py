#!/usr/bin/env python3
"""Project-task intake parser and QUE experiment-lane profiler (issue #3577).

The consumer workflow remains intake + receipt only: provider/model
selection and execution stay in existing dispatch machinery. This
module adds evidence-aware capability routing and experiment-lane
metadata without creating new canonical role names or claiming an
experiment has run.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

FIELDS = {
    "entry": "Entry",
    "task": "Task / spec",
    "scope": "Scope",
    "done-evidence": "Done-evidence",
    "target-repo": "Target repo",
    "instance-stamps": "Instance stamps (post-hoc)",
}
REQUIRED = ("entry", "task", "scope", "done-evidence")
DEFAULT_TARGET_REPO = "timerloggedout-spec/termux-monorepo"
NO_RESPONSE = "_No response_"
_HEADING = re.compile(r"^###\s+(.+?)\s*$", re.M)

# Canonical DoE epoch seats only. Specialist capability tags below are
# not new role IDs and never override the role registry.
CANONICAL_SEATS = ("builder", "operator", "steward", "observer",
                   "reviewer", "scout", "gambler", "participant")
SCIENTIFIC_TERMS = re.compile(
    r"\b(scien(?:ce|tific)|math(?:ematics|ematical)?|statistic(?:s|al)?|"
    r"experiment(?:al|ation)?|validation|causal inference|machine learning|"
    r"mlops|reproducib(?:le|ility)|numerical methods|formal methods)\b", re.I)
PSYCHOLOGY_TERMS = re.compile(
    r"\b(performance psychology|psycholog(?:y|ical)|momentum|motivation|"
    r"reinforcement|progressive challenge|feedback cycle|reward hacking)\b", re.I)
DO_STATEMENT_TERMS = re.compile(
    r"\bDO Statements?\b|\bstanding principle\b|\bprinciple of record\b", re.I)
FORBIDDEN_DATA_SENTINELS = ("N∅", "NOT_ESTABLISHED")
SPECIALIST_ROLE_MAP = {
    "scientific-quantitative": (
        "doe-expert", "research-scientist", "mathematician", "statistical-methodologist",
        "experiment-designer", "measurement-scientist", "ml-research-scientist",
        "ml-evaluation-specialist", "validation-engineer",
        "reproducibility-auditor",
    ),
    "do-statements": ("do-statement-methodologist", "behavioral-scientist"),
    "performance-psychology": (
        "performance-psychologist", "behavioral-scientist",
        "measurement-scientist", "experiment-designer",
    ),
}


def parse_issue_body(body: str) -> dict:
    by_label = {label: fid for fid, label in FIELDS.items()}
    sections = {}
    matches = list(_HEADING.finditer(body or ""))
    for i, match in enumerate(matches):
        label = match.group(1)
        if label not in by_label:
            continue
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        value = body[start:end].strip()
        sections[by_label[label]] = "" if value == NO_RESPONSE else value
    out = {fid: sections.get(fid, "") for fid in FIELDS}
    if not out["target-repo"]:
        out["target-repo"] = DEFAULT_TARGET_REPO
    return out


def validate(fields: dict) -> list:
    return [fid for fid in REQUIRED if not str(fields.get(fid, "")).strip()]


def profile_lanes(fields: dict) -> dict:
    """Derive candidate capability/experiment lanes from task text.

    Classification is advisory metadata: no provider is selected, no
    role is minted, and no campaign is promoted to preregistered merely
    because its keywords occur in an intake.
    """
    text = "\n".join(str(fields.get(k, "")) for k in ("task", "scope", "done-evidence"))
    lanes = []
    if SCIENTIFIC_TERMS.search(text):
        lanes.append("scientific-quantitative")
    if DO_STATEMENT_TERMS.search(text):
        lanes.append("do-statements")
    if PSYCHOLOGY_TERMS.search(text):
        lanes.append("performance-psychology")
    if "do-statements" in lanes and "performance-psychology" in lanes:
        lanes.append("do-statements-performance-psychology")
    specialist_roles = []
    for lane in lanes:
        for role_id in SPECIALIST_ROLE_MAP.get(lane, ()):
            if role_id not in specialist_roles:
                specialist_roles.append(role_id)
    return {
        "schema": "que-dispatch-profile/v1",
        "capability_lanes": lanes,
        "specialist_registry_ref": "ops/roles/scientific-specialists.json",
        "candidate_specialist_roles": specialist_roles,
        "specialist_roles_are_assignments": False,
        "experiment_lanes": [
            {"lane": lane, "state": "candidate_not_preregistered",
             "design_ref": None, "run_ref": None}
            for lane in lanes if lane in {
                "scientific-quantitative", "do-statements",
                "performance-psychology",
                "do-statements-performance-psychology"}
        ],
        "canonical_role_seats": list(CANONICAL_SEATS),
        "role_identity_is_provider_identity": False,
        "provider_selection": "existing_dispatch_policy",
        "siglary": {
            "standard_ref": "docs/proposals/active/notation-sets/SIGLARY-STANDARD.md",
            "enforcement": "required",
            "data_record_unknowns": None,
        },
    }


def validate_siglary_data_record(record: dict) -> list:
    """Reject Siglary's forbidden epistemic chat markers in data records."""
    encoded = json.dumps(record, ensure_ascii=False, sort_keys=True)
    return [token for token in FORBIDDEN_DATA_SENTINELS if token in encoded]


def receipt_comment(issue_number: int, fields: dict, profile: dict) -> str:
    lanes = profile["capability_lanes"] or ["general"]
    experiment_lines = [
        f"- {item['lane']}: `candidate_not_preregistered` "
        "(requires a committed DESIGN + run evidence before DoE admission)"
        for item in profile["experiment_lanes"]
    ] or ["- none inferred from this intake"]
    return (
        "[MUSEai]@{role:{project-task-dispatch}} ROUTING RECEIPT — "
        "task accepted into the system.\n\n"
        f"- intake id: issue #{issue_number}\n"
        f"- entry: {fields.get('entry', '')}\n"
        f"- scope: {fields.get('scope', '')}\n"
        f"- target repo: {fields.get('target-repo', '')}\n"
        f"- capability lanes: {', '.join(lanes)}\n"
        "- experiment lanes (candidate only):\n"
        + "\n".join(experiment_lines) + "\n"
        "- Siglary: required for dispatched participant stamps, "
        "outcome records and receipts; standard of record is "
        "`docs/proposals/active/notation-sets/SIGLARY-STANDARD.md`.\n"
        "- role seats: canonical DoE seats; capability tags do not mint roles\n"
        "- selection: system across all wired providers "
        "(no provider is named at intake, by design)\n"
        "- instance stamps: pending — filled post-hoc after execution "
        "{resolved provider × model · session/run ids · outcomes}\n\n"
        "Status: `dispatch-queued` — NOT owned until claimed.\n\n"
        "Claim/lease: the producing seat claims at pickup with "
        "`scripts/dispatch/claim_task.py` (claim comment + "
        "`dispatch-claimed` label). Unclaimed tasks are flagged at "
        "30 min and escalated at 60 min by the dispatch watchdog; "
        "filers route to a named seat in the same motion as the filing "
        "(interim rule, owner 2026-11-03)."
    )


def incomplete_comment(issue_number: int, missing: list) -> str:
    named = "\n".join(f"- `{FIELDS[fid]}`" for fid in missing)
    return (
        "[MUSEai]@{role:{project-task-dispatch}} INTAKE INCOMPLETE — "
        f"issue #{issue_number} is missing required field(s):\n\n"
        f"{named}\n\n"
        "Edit the issue to fill the field(s) above and the intake "
        "re-runs on reopen. Nothing was queued; no silent drops — "
        "this comment is the diagnosis.\n\n"
        "Status: `intake-incomplete`."
    )


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--body-file", required=True)
    ap.add_argument("--issue", required=True, type=int)
    ap.add_argument("--comment-out", required=True)
    ap.add_argument("--metadata-out")
    ap.add_argument("--github-output")
    args = ap.parse_args(argv)

    body = Path(args.body_file).read_text(encoding="utf-8")
    fields = parse_issue_body(body)
    missing = validate(fields)
    ok = not missing
    profile = profile_lanes(fields) if ok else None
    if profile and validate_siglary_data_record(profile):
        raise SystemExit("Siglary hard violation: forbidden epistemic marker in data record")
    comment = (receipt_comment(args.issue, fields, profile) if ok
               else incomplete_comment(args.issue, missing))
    Path(args.comment_out).write_text(comment + "\n", encoding="utf-8")
    if args.metadata_out and profile:
        Path(args.metadata_out).write_text(
            json.dumps(profile, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8")
    if args.github_output:
        with open(args.github_output, "a", encoding="utf-8") as fh:
            fh.write(f"ok={'true' if ok else 'false'}\n")
            fh.write(f"missing={','.join(missing)}\n")
            fh.write(f"capability_lanes={','.join(profile['capability_lanes']) if profile else ''}\n")
    print(f"intake #{args.issue}: ok={ok} missing={missing} lanes={profile['capability_lanes'] if profile else []}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
