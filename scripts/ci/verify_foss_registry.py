#!/usr/bin/env python3
"""Validate the FOSS foresight/procurement registry without third-party dependencies."""
from __future__ import annotations
import json, re
from pathlib import Path
from urllib.parse import urlparse
REGISTRY=Path("docs/ops/FOSS-FORESIGHT-PROCUREMENT-REGISTRY.json")
HORIZONS={'H0','H1','H2','H3'}; EVIDENCE={'CONFIRMED','ATTRIBUTED','EARLY_SIGNAL','SPECULATIVE'}; RISKS={'NONE','LOW','MEDIUM','HIGH','UNKNOWN'}; REPRO={'HIGH','MEDIUM','LOW','UNKNOWN'}
def fail(message): raise SystemExit(f'FOSS registry validation failed: {message}')
def main():
    try: registry=json.loads(REGISTRY.read_text(encoding='utf-8'))
    except (OSError,json.JSONDecodeError) as exc: fail(str(exc))
    if registry.get('schema_version')!='1.0': fail('unsupported schema_version')
    policy=registry.get('policy')
    if not isinstance(policy,dict) or policy.get('vendor_neutrality') is not True: fail('vendor_neutrality must remain true')
    if policy.get('secrets_allowed') is not False: fail('secrets_allowed must remain false')
    if policy.get('missing_evidence')!='null': fail("missing_evidence must be the literal policy marker 'null'")
    resources=registry.get('resources')
    if not isinstance(resources,list) or not resources: fail('resources must be non-empty')
    ids=set(); secret=re.compile(r'(?i)(api[_-]?key|token|password|secret|private[_-]?key)\s*[:=]')
    for r in resources:
        if not isinstance(r,dict): fail('resource must be an object')
        rid=r.get('id')
        if not isinstance(rid,str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]*',rid): fail(f'invalid id: {rid!r}')
        if rid in ids: fail(f'duplicate id: {rid}')
        ids.add(rid)
        if r.get('horizon') not in HORIZONS: fail(f'{rid}: invalid horizon')
        if r.get('evidence_status') not in EVIDENCE: fail(f'{rid}: invalid evidence_status')
        if r.get('lock_in_risk') not in RISKS or r.get('egress_risk') not in RISKS: fail(f'{rid}: invalid risk')
        if r.get('reproducibility') not in REPRO: fail(f'{rid}: invalid reproducibility')
        if not r.get('capabilities') or not r.get('procurement_action'): fail(f'{rid}: missing procurement fields')
        for u in r.get('canonical_sources',[]):
            p=urlparse(u)
            if p.scheme!='https' or not p.netloc: fail(f'{rid}: canonical source must be HTTPS: {u}')
        if secret.search(json.dumps(r,sort_keys=True)): fail(f'{rid}: credential-like material detected')
    print(f'validated {len(resources)} FOSS resources; vendor-neutrality=ON')
if __name__=='__main__': main()
