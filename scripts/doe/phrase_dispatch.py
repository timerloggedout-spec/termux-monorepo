#!/usr/bin/env python3
"""DoE phrase dispatch sender — live-3-phrases-deepseek execution leg.

Reads a committed dispatch job (schema doe-phrase-dispatch/v1: the
prompt was composed + stamped BEFORE dispatch by the campaign lane
via scripts/doe/phrase_layer.py; the composed text is hash-covered
by job.prompt_sha256) and sends it to OpenRouter chat completions.
The API key comes from the OPENROUTER_API_KEY env var only (Actions
secret); it is never printed, returned, or written to the result.

Writes a result JSON: {status, model_returned, usage, response_text,
response_sha256, timing}. Fails loud (nonzero exit + status=error in
the result file when writable) on transport/API errors — a failed
dispatch is a recorded outcome, never a silent retry.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE = "https://openrouter.ai/api/v1/chat/completions"
TIMEOUT = 900


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    job = json.loads(Path(args.job).read_text())
    result = {
        "schema": "doe-phrase-dispatch-result/v1",
        "campaign_id": job.get("campaign_id"),
        "dispatch_no": job.get("dispatch_no"),
        "model_requested": job.get("model"),
        "prompt_sha256": job.get("prompt_sha256"),
        "instance_key": job.get("instance_key"),
        "cell": (job.get("assignment") or {}).get("cell"),
        "status": "error",
        "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }

    def finish(code: int) -> int:
        result["finished_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
        Path(args.out).write_text(json.dumps(result, indent=1))
        print(f"dispatch {result['dispatch_no']}: status={result['status']}")
        if result.get("error"):
            print(f"dispatch error: {result['error']}")
        return code

    token = os.environ.get("OPENROUTER_API_KEY")
    if not token:
        result["error"] = "missing OPENROUTER_API_KEY env"
        return finish(2)

    payload = {
        "model": job["model"],
        "messages": [{"role": "user", "content": job["prompt"]}],
        "temperature": 0,
        "max_tokens": 6000,
    }
    req = urllib.request.Request(
        BASE, data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {token}",
                 "Content-Type": "application/json",
                 "User-Agent": "doe-phrase-dispatch/1"},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            body = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        result["error"] = f"http {e.code}: {e.read().decode(errors='replace')[:500]}"
        return finish(1)
    except Exception as e:  # transport, timeout, decode
        result["error"] = f"{type(e).__name__}: {e}"[:500]
        return finish(1)

    choices = body.get("choices") or []
    if not choices:
        result["error"] = f"no choices in response: {str(body)[:300]}"
        return finish(1)
    text = (choices[0].get("message") or {}).get("content") or ""
    result.update({
        "status": "ok",
        "model_returned": body.get("model"),
        "usage": body.get("usage"),
        "finish_reason": choices[0].get("finish_reason"),
        "response_text": text,
        "response_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "response_chars": len(text),
    })
    return finish(0)


if __name__ == "__main__":
    sys.exit(main())
