#!/usr/bin/env python3
"""Chat-provenance pipeline — session-history source class (owner req 2026-11-01).

Transforms per-surface chat exports into canonical `chat-provenance/v1`
records (ops/telemetry/session-history.jsonl, append-only, emit-once).
Consumers: ForeSight (canonical layer = open JSON/JSONL per
FORESIGHT-IMPLEMENTATION-STATUS) and 3L0 (mapping to 3l0-intake/v1,
origin="session-history", per docs/ops/3L0-PLANE.md charter amendment).

Capture routes (route field):
  api-token   API-driven surfaces (Muse runtime DB export; provider APIs)
  apk         on-device endpoints (Runable/DeepAgent class) — device emits
              rows in the same input shape; population lands when device
              lanes emit.
  webwrapper  web-surface collaborators (Grok/ChatGPT/GenSpark class) —
              wrapper session exports in the same input shape.

Input row: {chat_id, message_id, role, ts, body, route, surface_actor?,
            tool_events?} — tool_events carried verbatim when the route
exposes them; otherwise the record states the route limit honestly
(tool_calls: NOT_EXPOSED_BY_ROUTE; thinking: WITHHELD_BY_PLATFORM for
the Muse route — the platform withholds private reasoning by design).

Hard boundary: credential VALUES never enter payloads. Secret-shaped
values are scrubbed to [redacted:<kind>] before hashing or writing;
secret NAMES/refs are preserved.
"""
from __future__ import annotations

import hashlib, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import attribution as attribution_mod

SCHEMA = "chat-provenance/v1"

_SECRET_PATTERNS = [
    ("github-pat", re.compile(r"github_pat_[A-Za-z0-9_]{20,}")),
    ("github-token", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")),
    ("openai-key", re.compile(r"sk-[A-Za-z0-9_-]{20,}")),
    ("aws-key", re.compile(r"AKIA[A-Z0-9]{16}")),
    ("bearer", re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._-]{16,}")),
    ("api-key-value", re.compile(r"(?i)((?:api[_-]?key|token|secret|password)\s*[:=]\s*)\S{8,}")),
    ("jwt", re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{6,}")),
]


def scrub(text: str):
    n = 0
    out = text or ""
    for kind, rx in _SECRET_PATTERNS:
        def repl(m):
            nonlocal n
            n += 1
            return (m.group(1) if m.lastindex else "") + f"[redacted:{kind}]"
        out = rx.sub(repl, out)
    return out, n


def _actor_for(row, body):
    pseudo_pr = {"title": "", "body": body, "user": {"login": ""}}
    hit = attribution_mod.extract_actor(pseudo_pr)
    if hit["actor"]:
        return hit["actor"], hit["actor_evidence"]
    if row.get("role") == "assistant" and row.get("surface_actor"):
        return row["surface_actor"], {"method": "surface", "detail": {"route": row.get("route")}}
    if row.get("role") == "user":
        return "owner", {"method": "surface", "detail": {"role": "user"}}
    return None, {"method": None, "detail": {}}


def to_record(row, generated_at):
    body, redactions = scrub(row.get("body") or "")
    actor, evidence = _actor_for(row, body)
    actor, keyed = attribution_mod.apply_registry(actor)
    rec = {
        "schema": SCHEMA,
        "origin": "session-history",
        "route": row.get("route") or "api-token",
        "dispatch_id": f"sess:{row['chat_id']}:{row['message_id']}",
        "chat_id": row["chat_id"],
        "turn_anchor": row["message_id"],
        "ts": row.get("ts"),
        "role": row.get("role"),
        "actor": actor,
        "actor_evidence": evidence,
        "actor_registry_keyed": keyed,
        "content": body,
        "content_sha256": hashlib.sha256(body.encode()).hexdigest(),
        "content_chars": len(body),
        "redactions": redactions,
        "thinking": row.get("thinking", "WITHHELD_BY_PLATFORM"),
        "tool_calls": row.get("tool_events", "NOT_EXPOSED_BY_ROUTE"),
        "outcome": {"confirmed": None},
        "generated_at": generated_at,
    }
    return rec


def to_3l0(rec):
    """Map a chat-provenance record to the 3l0-intake/v1 shape (charter:
    observational by default; weights move only on confirmed != null)."""
    return {
        "schema": "3l0-intake/v1",
        "origin": "session-history",
        "dispatch_id": rec["dispatch_id"],
        "moniker": rec["actor"],
        "actor_evidence": rec["actor_evidence"],
        "ts": rec["ts"],
        "content_sha256": rec["content_sha256"],
        "outcome": {"confirmed": rec["outcome"]["confirmed"]},
    }


def emit(rows, existing_ids, generated_at):
    """Emit-once: skip dispatch_ids already in the feed."""
    out = []
    for row in rows:
        rec = to_record(row, generated_at)
        if rec["dispatch_id"] in existing_ids:
            continue
        existing_ids.add(rec["dispatch_id"])
        out.append(rec)
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", required=True, help="JSON list of export rows")
    ap.add_argument("--feed", default="ops/telemetry/session-history.jsonl")
    ap.add_argument("--now", default="1970-01-01T00:00:00Z")
    ap.add_argument("--receipt-out", default=None)
    args = ap.parse_args()
    rows = json.loads(Path(args.rows).read_text())
    feed = Path(args.feed)
    existing = set()
    if feed.exists():
        for line in feed.read_text().splitlines():
            if line.strip():
                existing.add(json.loads(line)["dispatch_id"])
    before = len(existing)
    new = emit(rows, existing, args.now)
    with feed.open("a") as fh:
        for rec in new:
            fh.write(json.dumps(rec, sort_keys=True, ensure_ascii=False) + "\n")
    receipt = {"feed": args.feed, "rows_in": len(rows), "emitted": len(new),
               "skipped_existing": len(rows) - len(new), "feed_total": before + len(new),
               "routes": sorted({r["route"] for r in new}),
               "redactions_total": sum(r["redactions"] for r in new)}
    if args.receipt_out:
        Path(args.receipt_out).write_text(json.dumps(receipt, indent=1, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
