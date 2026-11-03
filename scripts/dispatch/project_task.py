#!/usr/bin/env python3
"""Project-task intake parser (issue #3577).

Parses a GitHub issue-form body (the `project-task` form, or an
API-filed replica with the same `### Label` sections) into fields,
validates the required ones, and renders the routing-receipt or
intake-incomplete comment. The consumer workflow
(.github/workflows/project-task-dispatch.yml) is intake + receipt
only: selection/execution happens in the system's existing dispatch
machinery, never here — and never from a provider named at intake
(the form carries no provider field, by design).

CLI (workflow): reads the issue body from a file, writes the comment
to a file, and emits `ok` / `missing` step outputs.

    python3 project_task.py --body-file body.md --issue 3577 \
        --comment-out comment.md [--github-output $GITHUB_OUTPUT]
"""

from __future__ import annotations

import argparse
import re
import sys

# form field id -> rendered section label (must match
# .github/ISSUE_TEMPLATE/project-task.yml labels exactly)
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


def parse_issue_body(body: str) -> dict:
    """Split a rendered form body into {field_id: value}.

    Unknown sections are ignored; a field whose section is absent or
    rendered as `_No response_` maps to "".
    """
    by_label = {label: fid for fid, label in FIELDS.items()}
    sections = {}
    matches = list(_HEADING.finditer(body or ""))
    for i, m in enumerate(matches):
        label = m.group(1)
        if label not in by_label:
            continue
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        value = body[start:end].strip()
        if value == NO_RESPONSE:
            value = ""
        sections[by_label[label]] = value
    out = {fid: sections.get(fid, "") for fid in FIELDS}
    if not out["target-repo"]:
        out["target-repo"] = DEFAULT_TARGET_REPO
    return out


def validate(fields: dict) -> list:
    """Return the list of missing required field ids ([] = complete)."""
    return [fid for fid in REQUIRED if not str(fields.get(fid, "")).strip()]


def receipt_comment(issue_number: int, fields: dict) -> str:
    return (
        "[MUSEai]@{role:{project-task-dispatch}} ROUTING RECEIPT — "
        "task accepted into the system.\n\n"
        f"- intake id: issue #{issue_number}\n"
        f"- entry: {fields.get('entry', '')}\n"
        f"- scope: {fields.get('scope', '')}\n"
        f"- target repo: {fields.get('target-repo', '')}\n"
        "- selection: system across all wired providers "
        "(no provider is named at intake, by design)\n"
        "- instance stamps: pending — filled post-hoc after execution "
        "{resolved provider x model · session/run ids · outcomes}\n\n"
        "Status: `dispatch-queued` — NOT owned until claimed.\n\n"
        "Claim/lease: the producing seat claims at pickup with "
        "`scripts/dispatch/claim_task.py` (claim comment + "
        "`dispatch-claimed` label). Unclaimed tasks are flagged at "
        "30 min and escalated at 60 min by the dispatch watchdog; "
        "filers route to a named seat in the same motion as the "
        "filing (interim rule, owner 2026-11-03)."
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
    ap.add_argument("--github-output")
    args = ap.parse_args(argv)

    body = open(args.body_file, encoding="utf-8").read()
    fields = parse_issue_body(body)
    missing = validate(fields)
    ok = not missing
    comment = (receipt_comment(args.issue, fields) if ok
               else incomplete_comment(args.issue, missing))
    with open(args.comment_out, "w", encoding="utf-8") as fh:
        fh.write(comment + "\n")
    if args.github_output:
        with open(args.github_output, "a", encoding="utf-8") as fh:
            fh.write(f"ok={'true' if ok else 'false'}\n")
            fh.write(f"missing={','.join(missing)}\n")
    print(f"intake #{args.issue}: ok={ok} missing={missing}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
