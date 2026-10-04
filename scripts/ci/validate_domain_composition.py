#!/usr/bin/env python3
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
SEED = ROOT / 'docs/proposals/active/domain-composition-matrix/seed.json'
STATUSES = {'hypothesis','candidate','validated','deprecated','rejected'}
def fail(message):
    print('ERROR: ' + message, file=sys.stderr); raise SystemExit(1)
def main():
    data=json.loads(SEED.read_text(encoding='utf-8'))
    required=('schema_version','domains','operations','notations','composition_rules','evidence')
    for key in required:
        if key not in data: fail('missing top-level key: '+key)
    domains={x['domain_id']:x for x in data['domains']}
    operations={x['operation_id']:x for x in data['operations']}
    notations={x['notation_id']:x for x in data['notations']}
    for x in data['notations']:
        if x['domain_id'] not in domains: fail('notation references unknown domain')
        if x['operation_id'] not in operations: fail('notation references unknown operation')
        if x['status'] not in STATUSES: fail('invalid notation status')
    rule_ids=set()
    for x in data['composition_rules']:
        if x['rule_id'] in rule_ids: fail('duplicate rule_id: '+x['rule_id'])
        rule_ids.add(x['rule_id'])
        if x['domain_id'] not in domains or x['operation_id'] not in operations or x.get('notation_id') not in notations: fail('rule references unknown entity: '+x['rule_id'])
        if x['status'] not in STATUSES: fail('invalid rule status')
        if x.get('confidence') is not None and not 0 <= x['confidence'] <= 1: fail('invalid confidence')
    for x in data['evidence']:
        if x['rule_id'] not in rule_ids: fail('evidence references unknown rule')
    print(f"domain-composition: OK domains={len(domains)} operations={len(operations)} notations={len(notations)} rules={len(rule_ids)} evidence={len(data['evidence'])}")
if __name__ == '__main__': main()