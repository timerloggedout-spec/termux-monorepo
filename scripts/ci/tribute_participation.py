#!/usr/bin/env python3
"""Tribute participation loop — the required automation behind the
help-wanted / Tribute lane's upstream participation.

Owner order (2026-10-27): "This entire process is required Automations."
The manual pass this replaces is recorded in
docs/ops/TRIBUTE-LANE-EFFICACY-AUDIT-2026-10-27.md (Phase 2, batch 1).

Each run:
  1. Reads the lane universe from the tribute audit ledger
     (docs/ops/generated/help-wanted-tribute-audit.json; the status and
     audit rebuilds run as earlier workflow steps).
  2. Re-reads every actionable PR live and classifies it with
     decide_disposition() — deterministic, no LLM:
       held_surface            a maintainer's latest word to us is an
                               unanswered question or a change request.
                               The automation NEVER posts on these
                               (ROCm/rocm-libraries #13152 is the seed
                               case; replying is an owner-gated act).
       withdraw_nonconversion  our PR is open but its issue is closed —
                               a zombie stake. Apply: withdraw + close.
       withdraw_yield          issue is assigned to someone else, or a
                               human claimed it before we did.
                               Apply: withdraw + close.
       convert_candidate       stake-only PR, issue open and unclaimed —
                               engineering work for the contribute lane;
                               recorded, never auto-"fixed" with filler.
       active_ok               substantive PR awaiting upstream review.
       accepted_record         closed + merged (ledger bookkeeping).
       nonconversion_record    closed unmerged; stays a non-conversion.
       reopen_candidate        closed unmerged, but the issue is open,
                               unclaimed, and no maintainer closed the
                               PR as noise. Recorded for the reopen
                               pass; never auto-reopened in v1.
  3. Builds the claim ledger (G3 of the audit): issues carrying our
     claim comment, found by search (a floor — search undercounts this
     account — and labeled as such), each classified like a PR.
  4. Writes docs/ops/generated/tribute-participation.json. The workflow
     opens a refresh PR with the generated files; nothing here commits.

Apply-mode rails: only our own PRs are ever written to; only the two
withdraw classes execute; a per-run cap (default 10) defers the rest;
every action is re-read and verified before it is recorded as done.
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

US = "timerloggedout-spec"
STAKE_PATH = ".github/help-wanted-lane-stake.md"
CLAIM_MARKER = "Claim — termux-monorepo help-wanted lane"

WITHDRAW_NONCONVERSION_BODY = (
    "Withdrawing this stake PR: the linked issue is closed (resolved "
    "outside this PR), so this converts nothing. Recorded on our side "
    "as a non-conversion — closing to keep your queue clean. "
    "Apologies for the noise."
)
WITHDRAW_YIELD_BODY = (
    "Withdrawing this stake PR: a contributor is already engaged on "
    "the linked issue (assigned / applied / claimed before us), and "
    "our lane's rule is to yield to engaged humans. Closing to keep "
    "your queue clean — good luck with the fix."
)

CLAIM_INTENT_RE = re.compile(
    r"(has applied to work on this issue|i'?d like to work on this|"
    r"i would like to (work on|take|resolve)|can i (get assigned|work on this)|"
    r"please assign|i'?m working on|i am working on|working on this)",
    re.IGNORECASE,
)
QUESTION_RE = re.compile(r"\?\s*$", re.MULTILINE)
NOISE_RE = re.compile(
    r"(what is (the )?purpose of this|spam|noise|low[- ]effort|"
    r"placeholder|stake[- ]only|not a (real|actual) (fix|change|contribution))",
    re.IGNORECASE,
)


# ---------------------------------------------------------------- REST

class GH:
    def __init__(self, token):
        self.token = token

    def _req(self, method, path, body=None):
        url = "https://api.github.com" + path
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", f"Bearer {self.token}")
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("X-GitHub-Api-Version", "2022-11-28")
        if data:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req) as resp:
                raw = resp.read().decode()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"{method} {path} -> {e.code}") from e

    def get(self, path):
        return self._req("GET", path)

    def post(self, path, body):
        return self._req("POST", path, body)

    def patch(self, path, body):
        return self._req("PATCH", path, body)


# ------------------------------------------------------------- helpers

def parse_pr_url(url):
    m = re.match(r"https://github\.com/([^/]+/[^/]+)/pull/(\d+)", url or "")
    return (m.group(1), int(m.group(2))) if m else (None, None)


def parse_issue_ref(pr):
    """Best-effort linked issue for a lane PR: title 'for #N', then a
    body link to /issues/N in the same repo."""
    title = pr.get("title") or ""
    m = re.search(r"for #(\d+)", title)
    if m:
        return int(m.group(1))
    body = pr.get("body") or ""
    m = re.search(r"/issues/(\d+)", body)
    return int(m.group(1)) if m else None


def is_stake_only(file_paths):
    paths = [p for p in file_paths if p]
    return bool(paths) and all(p == STAKE_PATH for p in paths)


def is_bot(login):
    return login.endswith("[bot]") or login == "github-actions"


def human_comments(comments):
    return [c for c in comments if c["user"]["login"] != US and not is_bot(c["user"]["login"])]


def prior_human_claim(comments, our_first_ts):
    """A human staked a claim (assignment ask / wave application / 'I'm
    working on it') before our first visible activity on the issue."""
    for c in human_comments(comments):
        if our_first_ts and c["created_at"] >= our_first_ts:
            continue
        if CLAIM_INTENT_RE.search(c.get("body") or ""):
            return c["user"]["login"]
    return None


def maintainer_open_question(comments):
    """The latest human word on the thread is a question aimed at us
    that nobody (including us) has answered since."""
    ordered = sorted(comments, key=lambda c: c["created_at"])
    last_human = None
    for c in ordered:
        if c["user"]["login"] == US:
            last_human = None  # we spoke last; nothing is owed
            continue
        if not is_bot(c["user"]["login"]):
            last_human = c
    if last_human and QUESTION_RE.search((last_human.get("body") or "").strip()):
        return last_human["user"]["login"]
    return None


def maintainer_noise_flag(comments):
    for c in human_comments(comments):
        if NOISE_RE.search(c.get("body") or ""):
            return c["user"]["login"]
    return None


# ---------------------------------------------------------- classifier

def decide_disposition(pr, issue, comments, file_paths):
    """Pure classifier. pr/issue are REST dicts (issue may be None),
    comments are the PR-or-issue thread comments, file_paths the PR's
    changed paths. Returns (disposition, reason)."""
    state = pr.get("state")
    merged = bool(pr.get("merged_at"))
    our_first_ts = None
    for c in sorted(comments, key=lambda c: c["created_at"]):
        if c["user"]["login"] == US:
            our_first_ts = c["created_at"]
            break

    if state == "closed":
        if merged:
            return "accepted_record", "closed and merged upstream"
        if maintainer_noise_flag(comments):
            return "nonconversion_record", "maintainer flagged the PR itself; never reopen"
        if issue and issue.get("state") == "open":
            assignees = [a["login"] for a in issue.get("assignees", []) if a["login"] != US]
            if not assignees and not prior_human_claim(comments, our_first_ts):
                return "reopen_candidate", "issue open and unclaimed; PR was not closed as noise"
        return "nonconversion_record", "closed unmerged; issue closed, claimed, or unresolvable"

    # open PRs: a maintainer's open question freezes ALL automation on
    # the thread — including withdrawal. Replying is owner-gated.
    asker = maintainer_open_question(comments)
    if asker:
        return "held_surface", f"unanswered maintainer question from {asker}; owner-gated"

    if issue and issue.get("state") == "closed":
        return "withdraw_nonconversion", "linked issue is closed; the stake converts nothing"

    if issue:
        assignees = [a["login"] for a in issue.get("assignees", []) if a["login"] != US]
        if assignees:
            return "withdraw_yield", f"issue assigned to {', '.join(assignees)}"
        claimant = prior_human_claim(comments, our_first_ts)
        if claimant:
            return "withdraw_yield", f"human claim by {claimant} predates ours"

    if is_stake_only(file_paths):
        return "convert_candidate", "stake-only diff; issue open and unclaimed — needs a real fix"

    return "active_ok", "substantive diff; awaiting upstream review"


WITHDRAW = {
    "withdraw_nonconversion": WITHDRAW_NONCONVERSION_BODY,
    "withdraw_yield": WITHDRAW_YIELD_BODY,
}


def plan_actions(items, cap):
    """Items already classified; returns the subset to execute this run
    (withdraw classes only), capped, in input order."""
    planned = [i for i in items if i["disposition"] in WITHDRAW]
    return planned[:cap], len(planned) - min(len(planned), cap)


# ---------------------------------------------------------------- main

def load_json(path):
    with open(path) as fh:
        return json.load(fh)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["report", "apply"], default="report")
    ap.add_argument("--audit", default="docs/ops/generated/help-wanted-tribute-audit.json")
    ap.add_argument("--out", default="docs/ops/generated/tribute-participation.json")
    ap.add_argument("--max-actions", type=int, default=10)
    ap.add_argument("--max-closed", type=int, default=25)
    args = ap.parse_args(argv)

    token = (os.environ.get("OPERATOR_TOKEN") or os.environ.get("OPERATOR_GITHUB_TOKEN")
             or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"))
    if not token:
        print("no GitHub token in env (OPERATOR_TOKEN / GITHUB_TOKEN)", file=sys.stderr)
        return 2
    gh = GH(token)

    audit = load_json(args.audit)
    rows = audit.get("items", [])
    items, actions = [], []
    closed_seen = 0

    for row in rows:
        repo, num = parse_pr_url(row.get("pr_url"))
        if not repo:
            continue
        try:
            pr = gh.get(f"/repos/{repo}/pulls/{num}")
        except RuntimeError as e:
            items.append({"pr_url": row["pr_url"], "disposition": "unreachable",
                          "reason": str(e)})
            continue
        if pr["state"] == "closed":
            closed_seen += 1
            if closed_seen > args.max_closed and not pr.get("merged_at"):
                items.append({"pr_url": row["pr_url"], "disposition": "deferred_rotation",
                              "reason": "closed-set rotation cap; rechecked next runs"})
                continue
        files = []
        comments = []
        try:
            files = [f["filename"] for f in gh.get(f"/repos/{repo}/pulls/{num}/files?per_page=100")]
            comments = gh.get(f"/repos/{repo}/issues/{num}/comments?per_page=100")
        except RuntimeError:
            pass
        issue = None
        issue_num = parse_issue_ref(pr)
        if issue_num:
            try:
                issue = gh.get(f"/repos/{repo}/issues/{issue_num}")
                if issue.get("comments", 0) and not comments:
                    comments = gh.get(f"/repos/{repo}/issues/{issue_num}/comments?per_page=100")
            except RuntimeError:
                issue = None
        disposition, reason = decide_disposition(pr, issue, comments, files)
        item = {"pr_url": row["pr_url"], "disposition": disposition, "reason": reason,
                "issue_url": issue.get("html_url") if issue else None}
        items.append(item)

    planned, deferred = plan_actions(items, args.max_actions if args.mode == "apply" else 0)
    for item in planned:
        repo, num = parse_pr_url(item["pr_url"])
        try:
            gh.post(f"/repos/{repo}/issues/{num}/comments",
                    {"body": WITHDRAW[item["disposition"]]})
            gh.patch(f"/repos/{repo}/pulls/{num}", {"state": "closed"})
            check = gh.get(f"/repos/{repo}/pulls/{num}")
            ok = check["state"] == "closed"
        except RuntimeError as e:
            ok, item["action_error"] = False, str(e)
        item["action"] = "withdrawn" if ok else "action_failed"
        if ok:
            actions.append(item["pr_url"])

    # Claim ledger (G3): search floor, labeled as such.
    claims = []
    try:
        q = urllib.parse.quote(f"commenter:{US} type:issue")
        found = gh.get(f"/search/issues?q={q}&per_page=100")
        for it in found.get("items", []):
            repo_full = it["repository_url"].split("/repos/")[1]
            if repo_full.startswith(US + "/"):
                continue
            assignees = [a["login"] for a in it.get("assignees", []) if a["login"] != US]
            claims.append({
                "issue_url": it["html_url"],
                "state": it["state"],
                "assignees": assignees,
                "evidence": "search-floor; comment thread not re-read this run",
            })
    except RuntimeError as e:
        claims = [{"error": str(e)}]

    summary = {}
    for i in items:
        summary[i["disposition"]] = summary.get(i["disposition"], 0) + 1
    out = {
        "schema_version": "tribute-participation/v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": args.mode,
        "universe": "tribute audit ledger (help-wanted-tribute-audit.json)",
        "summary": summary,
        "actions_taken": actions,
        "withdrawals_deferred_by_cap": deferred if args.mode == "apply" else 0,
        "items": items,
        "claims": claims,
        "claims_note": "Claim enumeration is a search floor: GitHub search undercounts this account; rows are a minimum, not a census.",
    }
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps({"summary": summary, "actions": len(actions),
                      "claims": len(claims)}, indent=1))
    summary_md = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_md:
        with open(summary_md, "a") as fh:
            fh.write("## Tribute participation\n\n```json\n"
                     + json.dumps(summary, indent=1) + "\n```\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
