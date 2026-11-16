# L3VERAGE Department

**L3VERAGE = Leverage Engineering.** The Department designs and improves the mechanisms by which the agentic system converts capabilities, knowledge, coordination, automation, and measurement into verified outcomes.

## Start here

- [Department proposal](../proposals/active/l3verage-department/MANIFEST.md)
- [Work ledger](../proposals/active/l3verage-department/ITEMS.md)
- [Mechanism schema](MECHANISM.schema.json)
- [Mechanism hypothesis catalog](mechanisms.json)
- [Implementation plan](../superpowers/plans/2026-11-16-l3verage-department.md)

## Operating model

`DISCOVER → CLASSIFY → DESIGN → REGISTER → EXPERIMENT → VERIFY → PROMOTE → MONITOR → EVOLVE`

The department owns mechanism definitions and their lifecycle. Existing systems retain execution and evidence authority:

| Layer | Authority | L3VERAGE interaction |
|---|---|---|
| Opportunity discovery | CEEL + capability opportunity graph | Link candidate capability/opportunity IDs |
| Integration identity | Integration Intelligence | Reference integration IDs; no duplicate provider catalog |
| Experiment | DoE family / MVT | Pre-register treatment, control, cohort and stopping rule |
| Execution | ATES and existing workflows | Link attributed execution/run IDs |
| Quality/value | 3L0 / Moneyball and evaluator lanes | Compare correctness, quality, integration and outcomes |
| Evidence | Evidence envelope and canonical experiment schema | Store references, not duplicate run payloads |
| Approval | Proposal lifecycle, Delphi/EGM, dual gates | Submit candidates; do not bypass governance |

## Mechanism classes

- **Capability:** new or combined abilities that expand reliable outcomes.
- **Knowledge:** retrieval, context reuse, memory quality and provenance.
- **Coordination:** handoffs, routing, collaboration, contention and integration.
- **Automation:** repeatable workflows, recovery, idempotency and reduced manual toil.
- **Measurement:** attribution, observability, evaluation and decision confidence.

## Measurement

Each experiment declares its primary outcome, baseline, treatment, cohort, assignment, quality guardrails, resource vector, confounders, uncertainty and stop condition before execution.

The leverage ratio is:

`incremental validated outcome value ÷ incremental total resource cost`

Only compute it when both quantities are defined and comparable for the same eligible cohort. Report the underlying outcome and resource dimensions alongside the ratio. Do not compress multi-objective trade-offs into an unregistered weighted score; use Pareto comparisons where needed.

The Leverage Opportunity Index prioritizes hypotheses by expected impact, effort, confidence, reversibility and risk. It is a planning aid only and never evidence of realized value.

## Status discipline

A mechanism's presence in this catalog is not evidence of execution. Discovered, designed, admitted, experimenting, validated, promoted and monitored are distinct states. Seed entries are hypotheses. Validation and promotion require evidence references and existing approval/gate outcomes.

## Validate

```bash
python3 scripts/leverage/validate_mechanisms.py
python3 -m unittest discover -s tests -p 'test_leverage_mechanisms.py' -v
```
