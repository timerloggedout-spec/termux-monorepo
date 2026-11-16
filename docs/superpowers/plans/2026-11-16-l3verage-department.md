# L3VERAGE Department — implementation plan

**Proposal:** l3verage-department  
**Work items:** L3V-001 through L3V-006  
**Branch:** feat/l3verage-department-foundation  
**Base:** master

## Design decision

Build L3VERAGE as the intervention/mechanism discipline that composes existing department-grade systems. CEEL discovers capability opportunities; L3VERAGE turns selected opportunities into explicit, measurable interventions; DoE designs and runs comparisons; ATES records execution discipline; 3L0/Moneyball evaluates outcomes; canonical evidence envelopes preserve provenance; proposal governance and dual gates control promotion.

A small domain-specific mechanism catalog is justified because an intervention (trigger + treatment + expected outcome + guardrails) is not the same entity as an external integration or a capability opportunity. The catalog stores definitions and lifecycle pointers only. It does not store run telemetry.

## Tasks

1. Register the proposal and work ledger; add department navigation.
2. Add strict mechanism schema and seed hypothesis catalog with explicit discovered status.
3. Add a deterministic Python standard-library validator and unit tests.
4. Document measurement, leverage ratio, opportunity prioritization, guardrails and existing authority mappings.
5. Run focused tests and proposal/repository gates in CI; re-fetch checks on the same PR head.
6. Obtain independent review; admit a first pilot only through existing DoE and proposal processes.

## Acceptance and verification

- Catalog JSON parses and contains unique stable IDs.
- Lifecycle, class, resource dimensions and evidence references are validated.
- Validated/promoted/monitored claims require experiment identity and evidence references.
- Seed hypotheses remain discovered and have no fabricated execution evidence.
- Validator rejects malformed catalogs and returns nonzero.
- No new scheduler, telemetry envelope, integration registry, provider routing, deployment or external write is introduced.

## Commands

```bash
python3 scripts/leverage/validate_mechanisms.py
python3 -m unittest discover -s tests -p 'test_leverage_mechanisms.py' -v
python3 scripts/proposals/validate_registry.py
python3 scripts/ci/repo_gate.py
python3 scripts/ci/termux_smoke.py
```

The GitHub connector can write repository objects but cannot run the local checkout. CI results must be observed on the PR's immutable head SHA; queued/running is not a pass.
