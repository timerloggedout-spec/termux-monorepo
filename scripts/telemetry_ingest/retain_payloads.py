#!/usr/bin/env python3
"""Retain telemetry payloads into HindSight (live server contract).

Contract verified from the deployment's own source
(timerloggedout-spec/hindsight, hindsight_api/api/http.py):
  POST {HINDSIGHT_BASE_URL}/v1/default/banks/{bank_id}/memories
  Authorization: Bearer $HINDSIGHT_API_KEY
  body {"items": [{"content": str, "document_id": str, "context": str,
                   "metadata": {str: str}, "tags": [str]}],
        "async": true}
document_id gives upsert semantics: re-retaining the same unit updates
it in place, so refresh runs are idempotent. (The repo scaffold's
POST /retain shape in deepcli/_v1_hindsight.py is NOT a server route —
it failed 316/316 on 2026-10-31; see ingest receipt history.)

Failures are evidence, not stalls: the summary records the endpoint,
batch counts, and the first error's HTTP status + body excerpt so the
exact gate is reportable.
"""
from __future__ import annotations

import argparse, json, os, sys, urllib.error, urllib.request
from pathlib import Path
from urllib.parse import quote

BATCH = 50


def document_id_for(p: dict) -> str:
    md = p.get("metadata") or {}
    if md.get("source_id") and md.get("unit_id"):
        return f"telemetry:{md['source_id']}:{md['unit_id']}"
    if md.get("kind"):
        return "density:{}:{}".format(md["kind"], md.get("lane") or md.get("actor") or md.get("outcome_kind") or "global")
    return "telemetry:unknown"


def to_item(p: dict) -> dict:
    md = {str(k): str(v) for k, v in (p.get("metadata") or {}).items()}
    tags = ["telemetry-ingest"]
    if md.get("source_id"):
        tags.append(md["source_id"])
    if md.get("actor"):
        tags.append(f"actor:{md['actor']}")
    return {"content": p["content"], "document_id": document_id_for(p),
            "context": "telemetry-ingest", "metadata": md, "tags": tags}


def load_state(path):
    if path and Path(path).exists():
        return json.loads(Path(path).read_text())
    return {}


def retain(payloads, base, bank, key, batch=BATCH, opener=None, state=None, max_items=None):
    opener = opener or urllib.request.urlopen
    url = base.rstrip("/") + f"/v1/default/banks/{quote(str(bank), safe='')}/memories"
    summary = {"attempted": 0, "ok": 0, "failed": 0, "batches": 0, "batches_failed": 0,
               "endpoint": "POST /v1/default/banks/{bank_id}/memories",
               "first_error": None, "skipped_unchanged": 0}
    state = state if state is not None else {}
    fresh = []
    for p in payloads:
        doc = document_id_for(p)
        ev = (p.get("metadata") or {}).get("evidence_hash")
        if ev and state.get(doc) == ev:
            summary["skipped_unchanged"] += 1
        else:
            fresh.append(p)
    if max_items is not None:
        fresh = fresh[:max_items]
    items = [to_item(p) for p in fresh]
    ok_docs = []
    for i in range(0, len(items), batch):
        chunk = items[i:i + batch]
        summary["batches"] += 1
        summary["attempted"] += len(chunk)
        body = json.dumps({"items": chunk, "async": True}).encode()
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        if key:
            req.add_header("Authorization", f"Bearer {key}")
        try:
            with opener(req, timeout=60) as resp:
                if resp.status < 400:
                    summary["ok"] += len(chunk)
                    ok_docs += chunk
                else:
                    summary["failed"] += len(chunk); summary["batches_failed"] += 1
        except urllib.error.HTTPError as e:
            summary["failed"] += len(chunk); summary["batches_failed"] += 1
            if summary["first_error"] is None:
                try:
                    excerpt = e.read().decode(errors="replace")[:300]
                except Exception:
                    excerpt = ""
                summary["first_error"] = {"status": e.code, "body_excerpt": excerpt}
        except Exception as e:  # connection-level: record the class, no stall
            summary["failed"] += len(chunk); summary["batches_failed"] += 1
            if summary["first_error"] is None:
                summary["first_error"] = {"status": None, "body_excerpt": f"{type(e).__name__}: {e}"[:300]}
    for it in ok_docs:
        state[it["document_id"]] = it["metadata"].get("evidence_hash")
    summary["state"] = state
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", action="append", required=True)
    ap.add_argument("--receipt-out", default=None)
    ap.add_argument("--state", default=None,
                    help="json {document_id: evidence_hash} of already-retained units; "
                         "unchanged units are skipped (0 credit burn), state updated on success")
    ap.add_argument("--max-items", type=int, default=None)
    ap.add_argument("--batch", type=int, default=BATCH)
    args = ap.parse_args()
    base = os.environ.get("HINDSIGHT_BASE_URL")
    bank = os.environ.get("HINDSIGHT_BANK_ID")
    if not base or not bank:
        print(json.dumps({"skipped_reason": "HINDSIGHT_BASE_URL or HINDSIGHT_BANK_ID not set"}))
        return 0
    payloads = []
    for f in args.file:
        payloads += [json.loads(l) for l in Path(f).read_text().splitlines() if l.strip()]
    state = load_state(args.state)
    summary = retain(payloads, base, bank, os.environ.get("HINDSIGHT_API_KEY"),
                     batch=args.batch, state=state, max_items=args.max_items)
    if args.state:
        Path(args.state).write_text(json.dumps(summary.pop("state"), indent=1, sort_keys=True) + "\n")
    else:
        summary.pop("state", None)
    summary["payloads"] = len(payloads)
    if args.receipt_out:
        Path(args.receipt_out).write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n")
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
