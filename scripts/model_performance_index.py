#!/usr/bin/env python3
"""Outcome-first 3L0 performance index.

Correctness and integrated outcome dominate. Latency is a low-weight tiebreaker;
a fast incorrect answer must never beat a slower correct one. Skipped routes do
not count as model failures, and experiment identity prevents duplicate scoring.
"""
from __future__ import annotations
import json, math, statistics, sys
from collections import defaultdict

def percentile(values, p):
    if not values: return None
    values = sorted(values)
    if len(values) == 1: return values[0]
    rank = (len(values)-1)*p
    lo, hi = math.floor(rank), math.ceil(rank)
    return values[lo] if lo == hi else values[lo] + (values[hi]-values[lo])*(rank-lo)

def rate(values):
    known = [v for v in values if isinstance(v, bool)]
    return sum(known)/len(known) if known else None

def main():
    rows=[]
    for line in sys.stdin:
        if not line.strip(): continue
        row=json.loads(line)
        if row.get('route_status') not in {'attempted','failed','succeeded','skipped'}:
            raise SystemExit('invalid route_status')
        rows.append(row)
    unique={}
    for row in rows:
        key=row.get('experiment_id') or (
            row.get('repository'), row.get('workflow'), row.get('run_id'),
            row.get('run_attempt'), row.get('head_sha'), row.get('provider'),
            row.get('model'), row.get('role'), row.get('prompt_variant')
        )
        unique[key]=row
    groups=defaultdict(list)
    for row in unique.values():
        groups[(row.get('provider'),row.get('model'),row.get('role'))].append(row)
    result={'schema_version':2,'observations':len(unique),'models':[]}
    for (provider,model,role),items in sorted(groups.items()):
        attempted=[x for x in items if x['route_status'] in {'attempted','failed','succeeded'}]
        succeeded=[x for x in attempted if x['route_status']=='succeeded']
        lat=[x['latency_ms'] for x in attempted if isinstance(x.get('latency_ms'),(int,float))]
        req=[x['requests_used'] for x in attempted if isinstance(x.get('requests_used'),(int,float))]
        correctness=rate([x.get('correctness') for x in succeeded])
        integration=rate([x.get('integration_success') for x in succeeded])
        acceptance=rate([x.get('reviewer_acceptance') for x in succeeded])
        outcome=rate([x.get('task_success') for x in succeeded])
        quality_values=[x for x in (correctness,integration,acceptance,outcome) if x is not None]
        quality=statistics.mean(quality_values) if quality_values else None
        latency_score=None
        if lat:
            latency_score=1/(1+(percentile(lat,.95)/5000))
        # Outcome-first: correctness 40%, integration 30%, acceptance 20%,
        # task outcome 5%, latency only 5%. Missing quality fields are neutral,
        # not zeroes, so incomplete telemetry cannot manufacture a failure.
        score=None
        if quality is not None:
            parts=[
                .40*(correctness if correctness is not None else quality),
                .30*(integration if integration is not None else quality),
                .20*(acceptance if acceptance is not None else quality),
                .05*(outcome if outcome is not None else quality),
            ]
            parts.append(.05*(latency_score if latency_score is not None else quality))
            score=sum(parts)
        result['models'].append({
            'provider':provider,'model':model,'role':role,
            'attempts':len(attempted),'succeeded':len(succeeded),
            'skipped':sum(x['route_status']=='skipped' for x in items),
            'provider_failures':sum(x.get('error_class') in {'auth','rate_limit','provider','transport'} for x in attempted),
            'success_rate':len(succeeded)/len(attempted) if attempted else None,
            'correctness_rate':correctness,'integration_success_rate':integration,
            'task_success_rate':outcome,'reviewer_acceptance_rate':acceptance,
            'median_latency_ms':statistics.median(lat) if lat else None,
            'p95_latency_ms':percentile(lat,.95) if lat else None,
            'median_requests_used':statistics.median(req) if req else None,
            'execution_score_v2':score,
            'sample_status':'provisional' if len(attempted)<5 else 'rankable',
            'scoring_policy':'outcome_first_5pct_latency'
        })
    json.dump(result,sys.stdout,indent=2,sort_keys=True); sys.stdout.write('\n')

if __name__=='__main__': main()
