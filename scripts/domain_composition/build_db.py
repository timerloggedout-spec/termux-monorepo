#!/usr/bin/env python3
"""Materialize the versioned Domain Composition Matrix seed into SQLite."""
from __future__ import annotations
import argparse, json, sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"docs/proposals/active/domain-composition-matrix"
SCHEMA=BASE/"schema.sql"; SEED=BASE/"seed.json"; DEFAULT_DB=BASE/"domain-composition.sqlite"
def build(output: Path=DEFAULT_DB)->Path:
    data=json.loads(SEED.read_text(encoding="utf-8"))
    output.parent.mkdir(parents=True,exist_ok=True)
    if output.exists(): output.unlink()
    with sqlite3.connect(output) as db:
        db.executescript(SCHEMA.read_text(encoding="utf-8"))
        db.execute("INSERT INTO schema_version(version,applied_at,description) VALUES (?,datetime('now'),?)",(data["schema_version"],"Initial source-controlled research seed"))
        db.executemany("INSERT INTO domain(domain_id,name,parent_domain_id,description,status,version) VALUES (?,?,?,?,?,?)",[(x["domain_id"],x["name"],x.get("parent_domain_id"),x["description"],x["status"],x.get("version",1)) for x in data["domains"]])
        db.executemany("INSERT INTO entity_type(entity_type_id,domain_id,name,kind,description,version) VALUES (?,?,?,?,?,?)",[(x["entity_type_id"],x["domain_id"],x["name"],x["kind"],x["description"],x.get("version",1)) for x in data["entity_types"]])
        db.executemany("INSERT INTO operation(operation_id,canonical_name,semantic_family,description,version) VALUES (?,?,?,?,?)",[(x["operation_id"],x["canonical_name"],x["semantic_family"],x["description"],x.get("version",1)) for x in data["operations"]])
        db.executemany("INSERT INTO notation(notation_id,operation_id,domain_id,language,surface,canonical_form,description,status,version) VALUES (?,?,?,?,?,?,?,?,?)",[(x["notation_id"],x["operation_id"],x["domain_id"],x.get("language"),x["surface"],x.get("canonical_form"),x["description"],x["status"],x.get("version",1)) for x in data["notations"]])
        db.executemany("""INSERT INTO composition_rule
            (rule_id,domain_id,source_entity_type_id,operation_id,target_entity_type_id,result_entity_type_id,notation_id,precedence,associative,identity_required,valid,status,confidence,version)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",[(x["rule_id"],x["domain_id"],x["source_entity_type_id"],x["operation_id"],x["target_entity_type_id"],x.get("result_entity_type_id"),x.get("notation_id"),x.get("precedence"),x.get("associative"),x.get("identity_required"),x["valid"],x["status"],x.get("confidence"),x.get("version",1)) for x in data["composition_rules"]])
        db.executemany("INSERT INTO evidence(evidence_id,rule_id,source_ref,source_kind,locator,claim,observed_at,confidence) VALUES (?,?,?,?,?,?,?,?)",[(x["evidence_id"],x["rule_id"],x["source_ref"],x["source_kind"],x.get("locator"),x["claim"],x.get("observed_at"),x.get("confidence")) for x in data["evidence"]])
        db.commit()
    return output
if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=DEFAULT_DB)
    args=parser.parse_args()
    print(build(args.output))
