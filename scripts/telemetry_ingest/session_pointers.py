#!/usr/bin/env python3
"""Session-history POINTER exposure for pointer-reference validation.

Owner direction 2026-11-01 (via main): the Tests - LLM Validation lane
owns pointer-reference validation {resolves - hash-match - live} over
corpora incl. the sessions corpus. This builder exposes the pointer
fields of every session-history record in ONE correlation shape
(`ops/telemetry/session-pointers.jsonl`, schema session-pointer/v1) so
validation consumes one record per session row - no parallel index.

Derived, not intake: the file is REGENERATED from
`ops/telemetry/session-history.jsonl` each run (the feed is append-only,
so 1-based line numbers are stable pointers).

Contract (validation lane amendments A1-A3, 2026-11-01):
  - line index = index over NON-BLANK lines; the feed is blank-free by
    construction (the emitter never writes blank lines) and this builder
    ASSERTS blank-freedom rather than assuming it (A3).
  - line_sha256 = sha256(feed line as splitlines element, utf-8,
    NO trailing newline) (A2).
  - content_sha256 = sha256(record's content field, utf-8);
    content_chars = len(content str) (A2).
  - the receipt pins {feed_blob_sha (git blob sha1 of the feed file),
    generated_at} so an audit can name the exact feed version the
    pointers derive from (A1).

Per record:
  - feed pointer: {path, line, line_sha256}      -> resolves + hash-match
  - target pointer: muse-message {chat_id, turn_anchor=message_id} or
    github-pr-body {pr_number, turn_anchor}     -> resolves + live
  - content_sha256 (the feed record's own anchor) -> hash-match
Validation semantics live with the validation lane; this file only
exposes the pointers faithfully.

Usage: session_pointers.py --feed ops/telemetry/session-history.jsonl
         --out ops/telemetry/session-pointers.jsonl
         --receipt ops/telemetry/session-pointers-receipt.json
"""
import argparse
import hashlib
import json
import sys

SCHEMA = "session-pointer/v1"
FEED_PATH = "ops/telemetry/session-history.jsonl"


def target_for(rec: dict) -> dict:
    chat_id = rec.get("chat_id") or ""
    if chat_id.startswith("pr-"):
        try:
            pr = int(chat_id[3:])
        except ValueError:
            pr = None
        return {"kind": "github-pr-body", "pr_number": pr,
                "turn_anchor": rec.get("turn_anchor"),
                "resolution_route": "github pulls API (body)"}
    return {"kind": "muse-message", "chat_id": chat_id,
            "turn_anchor": rec.get("turn_anchor"),
            "resolution_route": "muse chat store (chat_id + message_id)"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--feed", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--receipt", required=True)
    args = ap.parse_args()

    raw_bytes = open(args.feed, "rb").read()
    raw = raw_bytes.decode("utf-8")
    all_lines = raw.splitlines()
    blanks = [i for i, l in enumerate(all_lines, start=1) if not l.strip()]
    assert not blanks, f"feed is not blank-free (blank lines: {blanks[:5]})"
    lines = all_lines
    feed_blob_sha = hashlib.sha1(
        b"blob " + str(len(raw_bytes)).encode() + b"\0" + raw_bytes
    ).hexdigest()
    out = []
    kinds = {}
    for i, line in enumerate(lines, start=1):
        rec = json.loads(line)
        tgt = target_for(rec)
        kinds[tgt["kind"]] = kinds.get(tgt["kind"], 0) + 1
        out.append({
            "schema": SCHEMA,
            "dispatch_id": rec["dispatch_id"],
            "feed": {"path": FEED_PATH, "line": i,
                     "line_sha256": hashlib.sha256(
                         line.encode("utf-8")).hexdigest()},
            "target": tgt,
            "content_sha256": rec.get("content_sha256"),
            "content_chars": rec.get("content_chars"),
            "actor": rec.get("actor"),
            "route": rec.get("route"),
            "ts": rec.get("ts"),
        })
    with open(args.out, "w", encoding="utf-8") as fh:
        for rec in out:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
    import datetime
    receipt = {"schema": SCHEMA, "feed": FEED_PATH, "records": len(out),
               "target_kinds": kinds,
               "feed_blob_sha": feed_blob_sha,
               "generated_at": datetime.datetime.now(
                   datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
               "consumer": "tests-llm-validation (pointer-reference validation)"}
    with open(args.receipt, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=1, sort_keys=True)
    print(json.dumps(receipt, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
