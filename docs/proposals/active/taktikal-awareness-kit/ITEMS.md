# Work Items — Taktikal Awareness Kit

| ID | Priority | Status | Scope | Acceptance criteria |
|---|---:|---|---|---|
| TAK-001 | P1 | proposed | Establish the T.A.K. architecture and system boundaries across RIDP, CRG, T.A.K., and Agentic Collaboration. | Architecture names canonical owners; no duplicate orchestrator, collector fleet, task ledger, or data lake; candidate picture surfaces remain candidates until formally bound. |
| TAK-002 | P1 | proposed | Define versioned entity, observation, relationship, and track-event contracts. | Schema validates source-scoped identity, event/capture times, provenance, evidence hash, source version, and epistemic status; ambiguous identity remains candidate. |
| TAK-003 | P1 | proposed | Define freshness, coverage, conflict, supersession, and uncertainty semantics for the common picture. | Tests prove stale/disconnected/unknown are not rendered as empty/zero; conflicting observations remain visible; all claims link to evidence or an explicit missing-evidence state. |
| TAK-004 | P1 | proposed | Build a read-only repository picture from existing GitHub, CI, CRG, dispatch-tree, tracking, and telemetry outputs. | One pinned SHA/run cohort; role-specific projections share canonical records; source coverage and as-of time are visible; no parallel collector is introduced. |
| TAK-005 | P1 | proposed | Integrate procurement/registration actor-network emergence with the existing repeat-crawl and receipt pipeline. | At least two approved sources; source receipts and versioned diffs; entity-resolution conflicts preserved; reproducible dataset version; no inferred affiliation presented as fact. |
| TAK-006 | P1 | proposed | Add OODA decision-support cards and human disposition feedback. | Each card names change, impact, evidence, freshness, uncertainty, owner, and next decision; execution routes only through existing Agentic Collaboration authorization. |
| TAK-007 | P1 | proposed | Calibrate signal quality and operational efficiency. | Frozen/adjudicated evaluation sample; measured precision/recall, freshness, latency, conflict rate, operator disposition, and useful outcomes; no invented baseline or savings claim. |

## Current disposition

Architecture and proposal package only. Runtime integration items remain proposed until implemented and independently validated. The owner-reported active awareness intent is recorded as operator context; concrete feed coverage and collector deployment remain to be evidenced by the owning lanes.
