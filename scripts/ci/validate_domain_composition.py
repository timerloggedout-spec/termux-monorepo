#!/usr/bin/env python3
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
SEED=ROOT/"docs/proposals/active/domain-composition-matrix/seed.json"
STATUSES={"hypothesis","candidate","validated","deprecated","rejected"}
def fail(message):
    print("ERROR: "+message,file=sys.stderr); raise SystemExit(1)
def main():
    data=json.loads(SEED.read_text(encoding="utf-8"))
    required=("schema_version","domains","entity_types","operations","notations","composition_rules","evidence")
    for key in required:
        if key not in data: fail("missing top-level key: "+key)
    domains={x["domain_id"]:x for x in data["domains"]}
    entities={x["entity_type_id"]:x for x in data["entity_types"]}
    operations={x["operation_id"]:x for x in data["operations"]}
    notations={x["notation_id"]:x for x in data["notations"]}
    if len(entities)!=len(data["entity_types"]): fail("duplicate entity_type_id")
    for x in data["entity_types"]:
        if x["domain_id"] not in domains: fail("entity_type references unknown domain: "+x["entity_type_id"])
    for x in data["notations"]:
        if x["domain_id"] not in domains: fail("notation references unknown domain")
        if x["operation_id"] not in operations: fail("notation references unknown operation")
        if x["status"] not in STATUSES: fail("invalid notation status")
    rule_ids=set()
    for x in data["composition_rules"]:
        rid=x["rule_id"]
        if rid in rule_ids: fail("duplicate rule_id: "+rid)
        rule_ids.add(rid)
        for key,table in (("domain_id",domains),("operation_id",operations),("notation_id",notations),("source_entity_type_id",entities),("target_entity_type_id",entities)):
            if x.get(key) not in table: fail(f"rule {rid} references unknown {key}: {x.get(key)}")
        result=x.get("result_entity_type_id")
        if result is not None and result not in entities: fail("rule references unknown result entity: "+rid)
        if x["status"] not in STATUSES: fail("invalid rule status")
        confidence=x.get("confidence")
        if confidence is not None and not 0 <= confidence <= 1: fail("invalid confidence: "+rid)
        if entities[x["source_entity_type_id"]]["domain_id"] != x["domain_id"]: fail("source entity crosses domain boundary: "+rid)
        if entities[x["target_entity_type_id"]]["domain_id"] != x["domain_id"]: fail("target entity crosses domain boundary: "+rid)
        if result is not None and entities[result]["domain_id"] != x["domain_id"]: fail("result entity crosses domain boundary: "+rid)
    for x in data["evidence"]:
        if x["rule_id"] not in rule_ids: fail("evidence references unknown rule")
    print(f"domain-composition: OK domains={len(domains)} entities={len(entities)} operations={len(operations)} notations={len(notations)} rules={len(rule_ids)} evidence={len(data['evidence'])}")
if __name__=="__main__": main()
