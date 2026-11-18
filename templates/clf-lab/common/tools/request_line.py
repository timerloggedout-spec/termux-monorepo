#!/usr/bin/env python3
"""DO print one mesh request line (clf-doe) for this lab repo ⇒ pipe into tools/append_jsonl.py.

Usage: request_line.py OWNER/REPO FAMILY [REF]
"""
import json
import sys
import time
from pathlib import Path

import yaml

repo, family = sys.argv[1], sys.argv[2]
ref = sys.argv[3] if len(sys.argv) > 3 else "main"
stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
args = {"repo": repo}
doe_path = Path(__file__).resolve().parent.parent / "doe.yaml"
if doe_path.exists():
    doe = yaml.safe_load(doe_path.read_text(encoding="utf-8"))
    ledger = doe_path.parent / "results" / "ledger.jsonl"
    done = set()
    if ledger.exists():
        done = {json.loads(l).get("cell_id") for l in ledger.read_text(encoding="utf-8").splitlines() if l.strip()}
    args.update({"gen": doe.get("generation"), "pending_cells": sum(1 for c in doe.get("cells", []) if c["id"] not in done),
                 "run": "python run_doe.py --node <name> --max-cells 4 --budget-s 900"})
print(json.dumps({"id": f"clf-{family}-{stamp}", "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                  "from": f"{repo.split('/')[-1]}:iterate", "target": "any", "kind": "clf-doe", "ref": f"{repo}@{ref}",
                  "priority": "T2", "args": args}, ensure_ascii=False))
