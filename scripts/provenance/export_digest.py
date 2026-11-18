#!/usr/bin/env python3
"""Provenance export digest — registered consumer of provenance-export-record/v1 (#5555, #5306).

DO read ingested records (JSONL) ⇒ publish an aggregate representation (¬ text, ¬ excerpts):
  per source_ns × export_class: records, classified share, label histogram per classifier,
  Actions comparison verdicts {consistent | claim-unevidenced | no-claim}.
DO record the read itself (consumer receipt) so utilization is demonstrated, ¬ asserted:
  one line per read → --reads JSONL {consumer, representation, source_ns, records, input_sha256, read_at}.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any

CONSUMER_ID = "provenance.export-digest/v1"
REPRESENTATION = "provenance-export-record/v1"


def digest(records: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, dict[str, Any]] = {}
    for r in records:
        key = f"{r.get('source_ns')}|{r.get('export_class')}"
        g = groups.setdefault(key, {"source_ns": r.get("source_ns"), "export_class": r.get("export_class"),
                                    "records": 0, "classified": 0, "labels": {}, "actions_verdicts": {},
                                    "credential_shapes": 0, "sessions": set()})
        g["records"] += 1
        g["sessions"].add(r.get("session"))
        g["credential_shapes"] += len(r.get("credentials") or [])
        if any(c.get("label") for c in r.get("classifications") or []):
            g["classified"] += 1
        for c in r.get("classifications") or []:
            lab = g["labels"].setdefault(str(c.get("classifier_id")), {})
            lab[str(c.get("label"))] = lab.get(str(c.get("label")), 0) + 1
        v = (r.get("actions") or {}).get("verdict", "unjoined")
        g["actions_verdicts"][v] = g["actions_verdicts"].get(v, 0) + 1
    out = []
    for g in sorted(groups.values(), key=lambda x: (str(x["source_ns"]), str(x["export_class"]))):
        g["sessions"] = len(g["sessions"])
        g["classified_share"] = round(g["classified"] / g["records"], 4) if g["records"] else None
        out.append(g)
    return {"schema": "provenance-export-digest/v1", "consumer": CONSUMER_ID, "representation": REPRESENTATION,
            "records": len(records), "groups": out}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Provenance export digest (consumer)")
    ap.add_argument("--records", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--reads", default="ops/provenance/consumer-reads.jsonl")
    a = ap.parse_args(argv)
    raw = Path(a.records).read_bytes()
    records = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    d = digest(records)
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    d["generated_at"] = now
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    receipt = {"consumer": CONSUMER_ID, "representation": REPRESENTATION,
               "source_ns": sorted({str(r.get("source_ns")) for r in records}), "records": len(records),
               "input_sha256": hashlib.sha256(raw).hexdigest(), "read_at": now}
    Path(a.reads).parent.mkdir(parents=True, exist_ok=True)
    with open(a.reads, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(receipt, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"::notice title=provenance-digest::records={len(records)} groups={len(d['groups'])} consumer={CONSUMER_ID}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
