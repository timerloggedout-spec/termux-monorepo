#!/usr/bin/env python3
"""EGM (Elephant-Goldfish) review template trigger.

Wraps the Elephant-Goldfish flow into the dispatch system as a
decision-triggered template, modeled on the #3577 project-task
trigger and parameterized on the DoE's pre-registered frame
(docs/ops/EGM-EVALUATION.md, PR #4210). Trigger spec:
docs/ops/EGM-TEMPLATE-TRIGGER.md.

Legs (stamped on the instance issue, in order):
  1. ELEPHANT — the owning seat posts an ELEPHANT PACKET
     (artifacts of record + referenced sources).
  2. GOLDFISH — >=2 zero-context reviewer seats post GOLDFISH
     CLAIMS (marker + zero-context attestation + reviewer seat),
     findings as claims in the frame's intake stamp {finding id
     · surface · reviewer seat · claim text · alleged location}.
  3. DOE VERIFICATION — MANDATORY, no bypass: DOE VERDICT
     comments {claim id · oracle · evidence · verdict} exit each
     claim VERIFIED / PARTIAL / REFUTED; only verified (and
     partial-restated) claims convert to scored RFPs; refuted
     claims score the reviewer's calibration.
  4. AWARDS — converted RFPs that win become route+claim build
     items (form + dispatch together, interim rule).

FAIL-CLOSED (inherited from upstream): if <2 genuinely fresh
(zero-context attested) reviewer seats arrive inside the claim
window, the review leg DOES NOT RUN — the sweep posts the
blocked record on the issue and labels it `egm-blocked`.
No theater: an understaffed review is recorded as not run.

CLI:
  intake: python3 egm_review.py --body-file body.md --issue N \
      --comment-out comment.md [--github-output $GITHUB_OUTPUT]
  sweep:  python3 egm_review.py sweep --repo owner/name \
      [--dry-run] [--token-env GITHUB_TOKEN]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

FIELDS = {
    "trigger-class": "Trigger class",
    "subject": "Subject under review",
    "elephant-seat": "Elephant seat",
    "artifacts": "Artifacts of record",
    "sources": "Referenced sources",
    "stakes": "Stakes",
    "claim-window": "Claim window (hours)",
}
REQUIRED = ("trigger-class", "subject", "elephant-seat",
            "artifacts", "stakes")
TRIGGER_CLASSES = ("design-decision", "new-surface-build",
                   "spec-design-draft")
NO_RESPONSE = "_No response_"
_HEADING = re.compile(r"^###\s+(.+?)\s*$", re.M)

PACKET_MARKER = "ELEPHANT PACKET"
CLAIMS_MARKER = "GOLDFISH CLAIMS"
VERDICT_MARKER = "DOE VERDICT"
BLOCKED_MARKER = "EGM BLOCKED — NO FRESH CONTEXT"
INSTANCE_LABEL = "egm-instance"
BLOCKED_LABEL = "egm-blocked"
ATTESTATION = "context consulted: artifacts + referenced sources only"
MIN_GOLDFISH = 2
VERDICTS = ("VERIFIED", "PARTIAL", "REFUTED")
# DoE hooks (frame = the template's evaluation core): runs are
# parameterized against the frame VERSION — stamps cite it, the
# machinery keys on it, the frame text is never copied in.
FRAME_VERSION = "egm-evaluation/v0"
CLAIM_STAMP = "egm_claim:"
VERDICT_STAMP = "egm_verdict:"
RUN_STAMP = "egm_run:"
ORACLES = ("source", "served", "test")
SEVERITIES = ("blocks-use", "degrades-use", "polish")

_CLAIM_ID = re.compile(r"claim id:\s*(\S+)", re.I)
_SEAT = re.compile(r"reviewer seat:\s*(.+)", re.I)
_VERDICT = re.compile(r"verdict:\s*(VERIFIED|PARTIAL|REFUTED)",
                      re.I)


def _stamp_fields(line: str) -> dict:
    """Parse the {k: v, ...} body of a one-line hook stamp."""
    body = line.split("{", 1)[1].rsplit("}", 1)[0]         if "{" in line and "}" in line else ""
    out = {}
    for part in body.split(","):
        if ":" in part:
            k, v = part.split(":", 1)
            out[k.strip()] = v.strip().strip('"')
    return out


def parse_claim_stamps(body: str) -> list:
    """egm_claim stamps pinned to the current frame version.
    A claim stamped against another frame version does not
    count — runs parameterize against the version."""
    claims = []
    for line in (body or "").splitlines():
        if CLAIM_STAMP not in line:
            continue
        f = _stamp_fields(line)
        if f.get("frame") != FRAME_VERSION:
            continue
        if f.get("claim_id") and f.get("reviewer_seat"):
            claims.append(f)
    return claims


def parse_verdict_stamps(body: str) -> list:
    """egm_verdict stamps, validated against the hook schema:
    oracle in {source|served|test}; severity REQUIRED on
    VERIFIED/PARTIAL (absent there = malformed, not counted)."""
    out = []
    for line in (body or "").splitlines():
        if VERDICT_STAMP not in line:
            continue
        f = _stamp_fields(line)
        if not f.get("claim_id"):
            continue
        if f.get("verdict") not in VERDICTS:
            continue
        if f.get("oracle") not in ORACLES:
            continue
        if f["verdict"] in ("VERIFIED", "PARTIAL") and                 f.get("severity") not in SEVERITIES:
            continue
        out.append(f)
    return out


def parse_issue_body(body: str) -> dict:
    by_label = {label: fid for fid, label in FIELDS.items()}
    sections = {}
    matches = list(_HEADING.finditer(body or ""))
    for i, m in enumerate(matches):
        label = m.group(1)
        if label not in by_label:
            continue
        start = m.end()
        end = (matches[i + 1].start() if i + 1 < len(matches)
               else len(body))
        value = body[start:end].strip()
        if value == NO_RESPONSE:
            value = ""
        sections[by_label[label]] = value
    out = {fid: sections.get(fid, "") for fid in FIELDS}
    if not out["claim-window"]:
        out["claim-window"] = "24"
    return out


def validate(fields: dict) -> list:
    missing = [fid for fid in REQUIRED
               if not str(fields.get(fid, "")).strip()]
    tc = str(fields.get("trigger-class", "")).strip()
    if tc and tc not in TRIGGER_CLASSES and \
            "trigger-class" not in missing:
        missing.append("trigger-class")
    return missing


def claim_window_hours(fields: dict) -> int:
    try:
        return max(1, int(str(fields.get("claim-window", "24"))
                          .strip() or 24))
    except ValueError:
        return 24


def receipt_comment(issue_number: int, fields: dict) -> str:
    window = claim_window_hours(fields)
    return (
        "[MUSEai]@{role:{egm-dispatch}} EGM INSTANCE — "
        "Elephant-Goldfish evaluation instantiated.\n\n"
        f"- instance: #{issue_number}\n"
        f"- trigger: {fields.get('trigger-class', '')}\n"
        f"- elephant seat: {fields.get('elephant-seat', '')}\n"
        f"- frame: docs/ops/EGM-EVALUATION.md (DoE, PR #4210)\n"
        f"- claim window: {window}h from the ELEPHANT PACKET\n"
        f"- goldfish minimum: {MIN_GOLDFISH} zero-context seats\n\n"
        "Legs, in order (each stamps this issue):\n"
        "1. ELEPHANT — the owning seat posts an `ELEPHANT PACKET` "
        "comment: the artifacts of record (at their merged SHAs) "
        "+ the referenced sources. Nothing reviews before the "
        "packet.\n"
        "2. GOLDFISH — >=2 reviewer seats with ZERO build context "
        "post `GOLDFISH CLAIMS` comments (artifacts + referenced "
        "sources ONLY), each carrying the attestation line "
        f"`{ATTESTATION}` and one hook stamp per finding: "
        "`egm_claim: {frame: \"egm-evaluation/v0\", instance, "
        "surface, artifact_sha, reviewer_seat, claim_id, "
        "alleged_location}` + the claim text.\n"
        "3. DOE VERIFICATION — MANDATORY, no bypass: the DoE leg "
        "posts one hook stamp per claim: `egm_verdict: {claim_id, "
        "oracle: source|served|test, verdict: VERIFIED|PARTIAL|"
        "REFUTED, evidence_ref, severity: blocks-use|degrades-use"
        "|polish (VERIFIED/PARTIAL only), verifier_seat}`. Only "
        "VERIFIED and PARTIAL-restated claims convert to scored "
        "RFPs; REFUTED claims score the reviewer's calibration "
        "(accuracy = (VERIFIED + ½·PARTIAL) / total claims).\n"
        "4. AWARDS — converted RFPs that win return as route+claim "
        "build items (project-task form + dispatch together, per "
        "the interim rule). When every claim carries a verdict "
        "the sweep posts the `egm_run:` close-out stamp {instance "
        "· claim counts V/P/R · per-seat reviewer calibration · "
        "scored set}.\n\n"
        "FAIL-CLOSED: if fewer than 2 fresh-context seats attest "
        f"within {window}h of the packet, the review leg does not "
        "run and the sweep records `EGM BLOCKED — NO FRESH "
        "CONTEXT` on this issue. No understaffed theater."
    )


def incomplete_comment(issue_number: int, missing: list) -> str:
    named = "\n".join(f"- `{FIELDS[fid]}`" for fid in missing)
    return (
        "[MUSEai]@{role:{egm-dispatch}} INTAKE INCOMPLETE — "
        f"issue #{issue_number} is missing/invalid field(s):\n\n"
        f"{named}\n\n"
        "Edit the issue to complete the field(s) and the intake "
        "re-runs on reopen. No instance was stamped; nothing was "
        "queued silently.\n\n"
        "Status: `intake-incomplete`."
    )


def _ts(comment: dict) -> datetime:
    raw = comment.get("created_at") or ""
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)


def evaluate(comments: list, now: datetime,
             window_hours: int = 24) -> dict:
    """Pure leg-state evaluation of one EGM instance.

    States: awaiting-packet · goldfish-open · doe-pending ·
    complete · blocked-no-fresh-context (window lapsed with
    <MIN_GOLDFISH attested seats). A seat counts ONLY from a
    GOLDFISH CLAIMS comment carrying the zero-context
    attestation AND >=1 egm_claim stamp pinned to the current
    frame version — memory-lessness is the method, so an
    unattested or off-frame review is not a goldfish. Verdicts
    count only as schema-valid egm_verdict stamps. When every
    claim carries a verdict the run is complete and the
    calibration table (per-seat (V + ½·P) / total) is computed
    for the egm_run close-out stamp.
    """
    packet_at = None
    seats = set()
    claim_seat = {}
    verdicts = {}
    blocked_posted = False
    run_posted = False
    for c in comments:
        body = c.get("body") or ""
        if PACKET_MARKER in body and packet_at is None:
            packet_at = _ts(c)
        if BLOCKED_MARKER in body:
            blocked_posted = True
        if RUN_STAMP in body:
            run_posted = True
        stamps = parse_claim_stamps(body)
        if CLAIMS_MARKER in body and ATTESTATION in body and \
                stamps:
            seats.update(st["reviewer_seat"] for st in stamps)
        for st in stamps:
            claim_seat[st["claim_id"]] = st["reviewer_seat"]
        for vs in parse_verdict_stamps(body):
            verdicts[vs["claim_id"]] = vs["verdict"]
    claims = sorted(claim_seat)
    calibration = {}
    for cid, seat in claim_seat.items():
        cal = calibration.setdefault(
            seat, {"claims": 0, "VERIFIED": 0, "PARTIAL": 0,
                   "REFUTED": 0, "accuracy": None})
        cal["claims"] += 1
        if cid in verdicts:
            cal[verdicts[cid]] += 1
    for cal in calibration.values():
        verdicted = (cal["VERIFIED"] + cal["PARTIAL"]
                     + cal["REFUTED"])
        if cal["claims"] and verdicted == cal["claims"]:
            cal["accuracy"] = round(
                (cal["VERIFIED"] + 0.5 * cal["PARTIAL"])
                / cal["claims"], 4)
    base = {"goldfish_seats": len(seats), "claims": len(claims),
            "verdicts": len(verdicts),
            "unverdicted": [c for c in claims
                            if c not in verdicts],
            "blocked_posted": blocked_posted,
            "run_posted": run_posted,
            "calibration": calibration,
            "counts": {v: sum(1 for x in verdicts.values()
                               if x == v) for v in VERDICTS}}
    if packet_at is None:
        return {**base, "state": "awaiting-packet"}
    if len(seats) >= MIN_GOLDFISH:
        state = ("complete" if claims and not base["unverdicted"]
                 else "doe-pending")
        return {**base, "state": state}
    if now > packet_at + timedelta(hours=window_hours):
        return {**base, "state": "blocked-no-fresh-context"}
    return {**base, "state": "goldfish-open"}


def run_closeout_comment(issue_number: int, ev: dict) -> str:
    cal = "; ".join(
        f"{seat}: claims {c['claims']} · V {c['VERIFIED']} · "
        f"P {c['PARTIAL']} · R {c['REFUTED']} · accuracy "
        f"{c['accuracy']}"
        for seat, c in sorted(ev["calibration"].items()))
    counts = ev["counts"]
    return (
        "[MUSEai]@{role:{egm-dispatch}} RUN CLOSE-OUT — every "
        "claim carries a verdict; the scored set (incl. REFUTED "
        "claims, published per the frame) converts from here.\n\n"
        f"{RUN_STAMP} {{instance: #{issue_number}, frame: "
        f"{FRAME_VERSION}, claims: {ev['claims']}, VERIFIED: "
        f"{counts['VERIFIED']}, PARTIAL: {counts['PARTIAL']}, "
        f"REFUTED: {counts['REFUTED']}, calibration: "
        f"{{{cal}}}}}\n\n"
        "Conversion: VERIFIED and PARTIAL-restated claims become "
        "scored RFPs in the delphi:rfp shape with their "
        "verification records carried in; award winners return "
        "as route+claim build items."
    )


def blocked_comment(ev: dict, window_hours: int) -> str:
    return (
        f"[MUSEai]@{{role:{{egm-dispatch}}}} {BLOCKED_MARKER} — "
        f"the claim window ({window_hours}h from the ELEPHANT "
        f"PACKET) closed with {ev['goldfish_seats']} attested "
        f"zero-context reviewer seat(s); the method requires "
        f"{MIN_GOLDFISH}.\n\n"
        "The review leg DID NOT RUN. Per the fail-closed rule "
        "inherited from upstream EGM, an understaffed review is "
        "recorded as not run — no findings exist for this "
        "instance, and none may be cited from it. Remedy: secure "
        ">=2 genuinely fresh reviewer seats and re-fire the "
        "template (a new instance), or extend the window by "
        "owner/DoE order on this issue and re-open."
    )


# ---------------- sweep (fail-closed enforcement) ----------------

def _request(method: str, path: str, token: str,
             payload: dict | None = None):
    url = "https://api.github.com" + path
    data = (json.dumps(payload).encode() if payload is not None
            else None)
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "egm-dispatch-sweep")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as resp:
        raw = resp.read().decode()
        return json.loads(raw) if raw.strip() else {}


def sweep(repo: str, token: str, now: datetime,
          apply: bool = True) -> list:
    issues = _request(
        "GET",
        f"/repos/{repo}/issues?labels=egm-review&state=open"
        f"&per_page=50", token)
    results = []
    for issue in issues:
        if "pull_request" in issue:
            continue
        num = issue["number"]
        comments = _request(
            "GET", f"/repos/{repo}/issues/{num}/comments"
            f"?per_page=100", token)
        fields = parse_issue_body(issue.get("body") or "")
        window = claim_window_hours(fields)
        ev = evaluate(comments, now, window)
        action = ""
        if ev["state"] == "complete" and not ev["run_posted"]:
            action = "post-run-closeout"
            if apply:
                _request("POST",
                         f"/repos/{repo}/issues/{num}/comments",
                         token,
                         {"body": run_closeout_comment(num, ev)})
        if ev["state"] == "blocked-no-fresh-context" and \
                not ev["blocked_posted"]:
            action = "post-blocked-record"
            if apply:
                _request("POST",
                         f"/repos/{repo}/issues/{num}/comments",
                         token, {"body": blocked_comment(ev, window)})
                _request("POST",
                         f"/repos/{repo}/issues/{num}/labels",
                         token, {"labels": [BLOCKED_LABEL]})
        results.append({"issue": num, **ev, "action": action})
    return results


def render_table(results: list) -> str:
    lines = ["issue | state | goldfish | claims | verdicts | action",
             "--- | --- | --- | --- | --- | ---"]
    for r in sorted(results, key=lambda r: r["issue"]):
        lines.append(
            f"#{r['issue']} | {r['state']} | {r['goldfish_seats']} "
            f"| {r['claims']} | {r['verdicts']} | "
            f"{r['action'] or '—'}")
    return "\n".join(lines)


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "sweep":
        ap = argparse.ArgumentParser(description=__doc__)
        ap.add_argument("sweep", help="run the fail-closed sweep")
        ap.add_argument("--repo", required=True)
        ap.add_argument("--dry-run", action="store_true")
        ap.add_argument("--token-env", default="GITHUB_TOKEN")
        args = ap.parse_args(argv)
        token = os.environ.get(args.token_env, "")
        if not token:
            print(f"error: ${args.token_env} is not set",
                  file=sys.stderr)
            return 2
        results = sweep(args.repo, token,
                        datetime.now(timezone.utc),
                        apply=not args.dry_run)
        print(render_table(results))
        return 0
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
    print(f"egm intake #{args.issue}: ok={ok} missing={missing}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
