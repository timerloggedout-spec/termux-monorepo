#!/usr/bin/env python3
"""Validate briefing evidence registries without third-party dependencies."""

from __future__ import annotations
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "briefing"

HORIZONS = {"H0","H1","H2","H3"}
EVIDENCE = {"confirmed","research","attributed","signal","speculative","disputed"}
DECISIONS = {"WATCH","INVESTIGATE","PROTOTYPE","ADOPT","REJECT","HOLD"}

def load_jsonl(path: Path):
    if not path.exists():
        return []
    raw = path.read_text()
    if "\\n" in raw and raw.count("\n") <= 1:
        chunks = [c for c in raw.split("\\n") if c.strip()]
    else:
        chunks = [ln for ln in raw.splitlines() if ln.strip()]
    rows = []
    for n, chunk in enumerate(chunks, 1):
        try:
            rows.append((n, json.loads(chunk)))
        except json.JSONDecodeError as e:
            raise SystemExit(f"{path}:{n}: invalid JSON: {e}")
    return rows

def uri(value):
    p = urlparse(value)
    return p.scheme in {"http","https"} and bool(p.netloc)

def require(row, keys, path, n):
    missing = [k for k in keys if k not in row]
    if missing:
        raise SystemExit(f"{path}:{n}: missing required fields: {', '.join(missing)}")

def validate_resources():
    required = ["resource_id","canonical_url","title","source_type","observed_at","evidence_status","horizon","confidence","claims"]
    seen = set()
    for n,r in load_jsonl(DATA/"resources.jsonl"):
        require(r, required, "resources.jsonl", n)
        if r["resource_id"] in seen:
            raise SystemExit(f"resources.jsonl:{n}: duplicate resource_id")
        seen.add(r["resource_id"])
        if not uri(r["canonical_url"]):
            raise SystemExit(f"resources.jsonl:{n}: invalid canonical_url")
        if r["horizon"] not in HORIZONS:
            raise SystemExit(f"resources.jsonl:{n}: invalid horizon")
        if r["evidence_status"] not in EVIDENCE:
            raise SystemExit(f"resources.jsonl:{n}: invalid evidence_status")
        if r["confidence"] not in {"high","medium","low"}:
            raise SystemExit(f"resources.jsonl:{n}: invalid confidence")

def validate_procurement():
    required = ["resource_id","project","canonical_source","license","maintenance","portability","offline_capability","interoperability","reproducibility","provenance","dependency_risk","lock_in_risk","security_surface","resource_cost","operational_fit","horizon","confidence","decision_status","version_or_commit","observed_at"]
    for n,r in load_jsonl(DATA/"procurement.jsonl"):
        require(r, required, "procurement.jsonl", n)
        if not uri(r["canonical_source"]):
            raise SystemExit(f"procurement.jsonl:{n}: invalid canonical_source")
        if r["decision_status"] not in DECISIONS:
            raise SystemExit(f"procurement.jsonl:{n}: invalid decision_status")
        if r["horizon"] not in HORIZONS:
            raise SystemExit(f"procurement.jsonl:{n}: invalid horizon")
        for target in ("arm64_linux","x86_64_linux","android","termux","offline_airgapped"):
            if target not in r["portability"]:
                raise SystemExit(f"procurement.jsonl:{n}: missing portability.{target}")
        for lock in ("runtime","evidence"):
            if lock not in r["lock_in_risk"]:
                raise SystemExit(f"procurement.jsonl:{n}: missing lock_in_risk.{lock}")

def validate_radar():
    required = ["signal_id","title","horizon","evidence_status","enabling_technologies","convergence","bottlenecks","strategic_dependencies","foss_alternatives","prototype_concepts","procurement_implications","lock_in_exposure","termux_relevance","confidence"]
    for n,r in load_jsonl(DATA/"radar.jsonl"):
        require(r, required, "radar.jsonl", n)
        if r["horizon"] not in HORIZONS:
            raise SystemExit(f"radar.jsonl:{n}: invalid horizon")
        if r["evidence_status"] not in EVIDENCE:
            raise SystemExit(f"radar.jsonl:{n}: invalid evidence_status")

def main():
    validate_resources()
    validate_procurement()
    validate_radar()
    print("briefing registry validation: OK")

if __name__ == "__main__":
    main()
