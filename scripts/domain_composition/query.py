#!/usr/bin/env python3
"""Read-only query surface for the materialized Domain Composition Matrix."""
from __future__ import annotations
import argparse, sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
DB=ROOT/"docs/proposals/active/domain-composition-matrix/domain-composition.sqlite"
def main():
    p=argparse.ArgumentParser(); p.add_argument("--status",choices=["hypothesis","candidate","validated","deprecated","rejected"]); p.add_argument("--domain"); a=p.parse_args()
    if not DB.exists(): raise SystemExit("database not materialized; run scripts/domain_composition/build_db.py")
    where=[]; params=[]
    if a.status: where.append("r.status = ?"); params.append(a.status)
    if a.domain: where.append("r.domain_id = ?"); params.append(a.domain)
    clause=(" WHERE "+" AND ".join(where)) if where else ""
    sql=f"""SELECT r.rule_id,r.domain_id,r.source_entity_type_id,r.operation_id,r.target_entity_type_id,n.surface,r.status,r.confidence
            FROM composition_rule r LEFT JOIN notation n ON n.notation_id=r.notation_id {clause} ORDER BY r.rule_id"""
    with sqlite3.connect(DB) as db:
        for row in db.execute(sql,params): print("\\t".join("" if v is None else str(v) for v in row))
if __name__=="__main__": main()
