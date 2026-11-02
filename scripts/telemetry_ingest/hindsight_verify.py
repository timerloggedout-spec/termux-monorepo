#!/usr/bin/env python3
"""Verify HindSight population after a retain proof/full run.

Reads (no writes, no credit burn beyond one recall):
  GET  {base}/health
  GET  {base}/v1/default/banks/{bank}/stats
  GET  {base}/v1/default/banks/{bank}/llm-requests/stats
  POST {base}/v1/default/banks/{bank}/memories/recall  {query}
Prints a JSON evidence summary; exit code is always 0 — the summary is
the gate evidence, callers decide on it.
"""
from __future__ import annotations

import argparse, json, os, urllib.request
from urllib.parse import quote


def _call(opener, req):
    try:
        with opener(req, timeout=30) as resp:
            raw = resp.read().decode(errors="replace")
            try:
                return {"status": resp.status, "json": json.loads(raw)}
            except Exception:
                return {"status": resp.status, "text": raw[:300]}
    except Exception as e:
        code = getattr(e, "code", None)
        body = ""
        try:
            body = e.read().decode(errors="replace")[:300]
        except Exception:
            body = f"{type(e).__name__}: {e}"[:300]
        return {"status": code, "error": body}


def verify(base, bank, key, query="telemetry ingest coverage providers", opener=None):
    opener = opener or urllib.request.urlopen
    root = base.rstrip("/")
    b = quote(str(bank), safe="")
    out = {}
    def req(method, url, body=None):
        r = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None,
                                   method=method, headers={"Content-Type": "application/json"})
        if key:
            r.add_header("Authorization", f"Bearer {key}")
        return _call(opener, r)
    out["health"] = req("GET", f"{root}/health")
    out["bank_stats"] = req("GET", f"{root}/v1/default/banks/{b}/stats")
    out["llm_stats"] = req("GET", f"{root}/v1/default/banks/{b}/llm-requests/stats")
    out["recall_probe"] = req("POST", f"{root}/v1/default/banks/{b}/memories/recall", {"query": query})
    st = (out["bank_stats"].get("json") or {})
    out["memories_total"] = st.get("total_memories") or st.get("memories") or st.get("count")
    rec = (out["recall_probe"].get("json") or {})
    results = rec.get("results") or rec.get("memories") or []
    out["recall_hits"] = len(results) if isinstance(results, list) else None
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", default="telemetry ingest coverage providers")
    ap.add_argument("--receipt-out", default=None)
    args = ap.parse_args()
    base = os.environ.get("HINDSIGHT_BASE_URL")
    bank = os.environ.get("HINDSIGHT_BANK_ID")
    if not base or not bank:
        print(json.dumps({"skipped_reason": "HINDSIGHT_BASE_URL or HINDSIGHT_BANK_ID not set"}))
        return 0
    out = verify(base, bank, os.environ.get("HINDSIGHT_API_KEY"), args.query)
    if args.receipt_out:
        from pathlib import Path
        Path(args.receipt_out).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: out[k] for k in ("memories_total", "recall_hits")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
