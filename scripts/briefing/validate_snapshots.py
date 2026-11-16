#!/usr/bin/env python3
"""Validate dated five-item briefing snapshots against the repository contract."""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[2]
DIR=ROOT/"data"/"briefing"/"briefings"
HORIZONS={"H0","H1","H2","H3"}
EVIDENCE={"confirmed","research","attributed","signal","speculative","disputed"}
REQUIRED={"headline","horizon","evidence_status","summary","why_it_matters","opportunity_or_procurement","monorepo_relevance","sources","confidence","image_query"}

def main():
    files=sorted(DIR.glob("*.json"))
    if not files:
        raise SystemExit("no briefing snapshots found")
    for p in files:
        row=json.loads(p.read_text())
        if not isinstance(row,dict):
            raise SystemExit(f"{p}: snapshot must be object")
        items=row.get("items")
        if not isinstance(items,list) or len(items)!=5:
            raise SystemExit(f"{p}: expected exactly five items")
        if row.get("briefing_date") != p.stem:
            raise SystemExit(f"{p}: briefing_date does not match filename")
        datetime.fromisoformat(row["generated_at"].replace("Z","+00:00")).astimezone(timezone.utc)
        for i,item in enumerate(items,1):
            missing=REQUIRED-set(item)
            if missing: raise SystemExit(f"{p}:{i}: missing {sorted(missing)}")
            if item["horizon"] not in HORIZONS: raise SystemExit(f"{p}:{i}: invalid horizon")
            if item["evidence_status"] not in EVIDENCE: raise SystemExit(f"{p}:{i}: invalid evidence_status")
            if item["confidence"] not in {"high","medium","low"}: raise SystemExit(f"{p}:{i}: invalid confidence")
            if not item["sources"]: raise SystemExit(f"{p}:{i}: no sources")
            if not item["image_query"].strip(): raise SystemExit(f"{p}:{i}: image_query empty")
        for signal in row.get("radar_watch",[]):
            if signal.get("horizon") not in {"H2","H3"}:
                raise SystemExit(f"{p}: radar_watch signal must be H2/H3")
    print(f"daily briefing snapshot validation: OK ({len(files)} snapshots)")
if __name__=="__main__":
    main()
