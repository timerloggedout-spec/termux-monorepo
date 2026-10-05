#!/usr/bin/env python3
"""Strict tunnel+hub health probe. Exit 0 on real health, 1 on failure.

Positive contract: probe returns 200 for /v1/models and /health.
"""
from __future__ import annotations
import pathlib, sys, urllib.error, urllib.request

PATHS = ("/v1/models", "/health")
TIMEOUT = 8

def probe(base, path):
    url = base.rstrip("/") + path
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.status, url
    except urllib.error.HTTPError as exc:
        return exc.code, url
    except Exception:
        return 0, url

def main(argv):
    if len(argv) < 2:
        print(__doc__); return 2
    mode = argv[1]
    if mode == "local":
        base = "http://127.0.0.1:8800"
    elif mode == "external" and len(argv) >= 3:
        base = pathlib.Path(argv[2]).read_text().strip()
    elif mode == "url" and len(argv) >= 3:
        base = argv[2]
    else:
        print(__doc__); return 2
    print("probing " + base)
    ok = True
    for path in PATHS:
        code, url = probe(base, path)
        mark = "PASS" if code == 200 else "FAIL"
        print("  [" + mark + "] " + url + "  ->  " + str(code))
        if code != 200: ok = False
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
