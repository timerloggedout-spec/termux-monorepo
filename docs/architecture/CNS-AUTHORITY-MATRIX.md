# CNS Authority Matrix

**Status:** Initial canonical ownership map  
**Source ref:** `master@939ecc225675541d1ad5b829b427c7ac77ac2642`

The CNS coordinates independently governed organs. Each mutable domain retains one canonical owner. CNS registry, integration map, health model, and SHE views provide metadata projections.

| Domain / state | Canonical owner | CNS relationship | Permission / evidence boundary |
|---|---|---|---|
| Proposal lifecycle and governance | Repository governance: `docs/proposals/PROCESS.md`, `registry.yaml` | CNS proposal is registered through this lifecycle | Operator authorization and proposal states govern execution |
| Task context and navigation | ICM | Supplies bounded context to Manager and Brain | Source records and scope registry remain canonical |
| Relationship graph and evidence edges | CRG | Supplies provenance and temporal relationships | Verified/derived/inferred/candidate classifications remain distinct |
| Reasoning stages | Brain kernel | Produces typed reasoning and advisory handoffs | Host owns invocation; policy owner retains policy authority |
| Specialist extensions | MOSAIC / specialist contracts | Supplies bounded domain reasoning | Extension contract governs compatibility |
| Task admission and execution claims | QUE / QDesk | Receives manager-approved tasks | Existing queue and execution claim authority |
| Dependency readiness | Ballet | Supplies dependency-wave readiness | Readiness is admission evidence, not provider selection |
| Work sequencing and escalation | Manager / Conductor | Coordinates cross-organ work | Operates within repository permission and approval rules |
| Provider/model selection | Provider Router | Consumes eligibility and score evidence | Real adapter and admission contract required |
| Context admission and arbitration | SHIELD / ORBIT | Observe-only proposal until integrated | PR #5544; any authority transition requires governed acceptance |
| Event interoperability | Synaptic Bus | Correlation and canonical record references | PR #5637; event owners retain canonical records |
| Runtime execution evidence | ATES / Action-Effect / workflow records | Supplies evidence to CNS health and learning projections | Observed events and artifacts remain source of truth |
| Actor performance scoring | 3L0 | Supplies actor eligibility and weighting evidence | 3L0 owns actor scores and records |
| PR quality scoring | MoneyBall | Supplies PR score and quota multiplier | MoneyBall owns PR records; separate from 3L0 |
| Experiment design and evaluation | DoE / MVT | Supplies comparative evidence | Treatment identity and outcomes remain attributable |
| Skill and policy evolution | Governed skill / Manager evolution process | Consumes repeated evidence | Changes follow proposal, review, tests, and promotion gates |
| Dashboard snapshots | SHE reducers and snapshot pipeline | Presents read-only CNS state | Source SHA, snapshot ID, generation time, coverage |
| Historical exploration | CRG + Historical Corpus Explorer | Read-only temporal projection | CRG manifest, schemas, and immutable snapshot lineage |
| Credentials and secrets | Existing repository secret and permission owners | CNS stores names and references only | Credential values stay in approved secret stores |
| Review and merge | GitHub branch protection / repository governance | CNS reports state and evidence | Dual gates and authorized promotion path |
| Release and deployment | Existing release/deployment owners | CNS observes deployment receipts | Deployment permission and provenance remain canonical |
| Writer lease | Unassigned enforcement authority (proposed) | Would gate revision-bound corrective writes | Global provider enforcement remains unimplemented and unverified |

## Authority rules

1. Each mutable domain has one canonical owner.
2. A consumer reads canonical records through a versioned contract or explicit adapter.
3. A projection records source identity and freshness.
4. A provider catalog entry becomes executable only through a configured adapter and admission contract.
5. A reasoning result remains advisory until the owning workflow accepts its handoff.
6. A score is evidence for selection; it is not a dispatch command.
7. A green check is workflow evidence; task outcome remains a separate classification.
8. Promotion follows the repository's proposal lifecycle, dual gates, and permission model.
