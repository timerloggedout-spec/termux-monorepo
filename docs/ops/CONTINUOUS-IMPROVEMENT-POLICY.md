# Continuous Improvement Policy — ATES × TDQS × Evidence Ops

**Policy status:** active learning contract  
**Scope:** agent evaluation, tool-definition quality, repository administration, workflow orchestration  
**Principle:** templates, resources, prior implementations, reviews, and external skills are learning inputs for custom adaptation.

## 1. Learning loop

**Observe → Contextualize → Adapt → Implement → Verify → Record → Recompare → Repeat**

- Observe: collect current-SHA evidence and relevant historical/template evidence.
- Contextualize: use the context-relationship graph and exact roots; separate verified relationships from candidates.
- Adapt: extract the smallest transferable contract; do not copy assumptions, permissions, metrics, or infrastructure blindly.
- Implement: make one bounded change.
- Verify: run deterministic tests and relevant GitHub workflow gates.
- Record: preserve source/version, adaptation, evidence, outcome, and remaining uncertainty.
- Recompare: compare the new version with its predecessor and applicable upstream/template contract.
- Repeat: continue only while evidence shows a useful delta.

## 2. Template/resource adoption

A template or resource may progress through: REFERENCE → ADAPTED → VALIDATED → ADOPTED → SUPERSEDED.

Record source, version/commit/date, relevant contract, local adaptation, permission/safety impact, validation evidence, supersession, and remaining uncertainty.

## 3. Curated lessons incorporated

### Loopy / loop-library pattern

Retain the transferable mechanics: bounded six-step cycles, explicit terminal states, current-state re-read before consequential actions, verification under recorded conditions, run receipts, measurable-progress stopping, and separation of crafting from execution.

Local adaptation: adaptive-wait turns WAIT into evidence collection with adaptive cadence and SHA-bound re-fetches; evidence-led-monorepo-ops owns repository closeout.

### Context Relationship Graph

Retain exact-root reconnaissance, metadata-only collection, verified/candidate separation, native timeline/direct-permalink evidence, bounded history, explicit omissions, and trusted publication boundaries.

Local adaptation: CRG remains the relationship-evidence owner; adaptive-wait consumes that evidence without duplicating the graph.

### Jules / asynchronous coding-agent patterns

Retain asynchronous implementation, issue/PR/review-driven feedback, tests before promotion, provider identity as provenance, and bounded follow-up.

Local adaptation: asynchronous agents are evidence-producing collaborators, not implicit authority to merge, rewrite policy, or suppress findings. Current-SHA evidence and repository gates remain authoritative.

### Termux MCP project stewardship

Retain lean-worktree discipline, read-only-by-default reconnaissance, device/resource preflight, explicit mutation boundaries, and operational health evidence.

Local adaptation: these constraints apply when the Termux/MCP hub is the execution surface; repository governance remains authoritative.

## 4. ATES + TDQS semantic contract

Tool definition → TDQS; agent execution → ATES; both feed the AEF evidence unit and downstream outcome analysis.

- TDQS: quality of the tool definition exposed to an agent.
- ATES: observational execution/throughput telemetry.
- AEF: evidence/evaluation-unit boundary.
- 3L0/WTCV/TCV: downstream repository-defined aggregation/decision surfaces.

TDQS is never task correctness or agent quality. ATES is never a speed-only merge gate.

## 5. Version comparison

When a rubric/template evolves, preserve both versions and compare semantic changes, weights/formulas, required evidence, safety/permission boundaries, schema changes, workflow impact, migration/backfill implications, compatibility, and regressions.

For TDQS, the imported external reference is v1.3. Preserve provenance and do not silently claim a local fork is identical when it differs.

## 6. Evidence and promotion

A green workflow proves that workflow's checks; it does not prove the requested outcome.

Promotion requires current immutable SHA, current base/merge relationship, relevant validation terminal, review/finding disposition, task-outcome evidence, and repository-defined dual gates.

Terminal states: success | clean-no-op | blocked | approval-required | exhausted | stagnated.

Never convert provider failure, skipped review, rate limit, stale SHA, or infrastructure/browser failure into correctness success.

## 7. Reusable adaptation template

### Source
- name / URL or path / version or commit / observed date

### Transferable contract
- useful behavior / evidence supporting it

### Local adaptation
- changed semantics / permission boundary / repository owner / policy conflicts

### Validation
- deterministic test / workflow run / current SHA / outcome

### Version comparison
- previous / current / changed / migration

### Decision
- REFERENCE | ADAPTED | VALIDATED | ADOPTED | SUPERSEDED
- remaining uncertainty

## 8. Anti-patterns

Do not dismiss useful lessons solely because they are external; copy external policy without local validation; conflate activity with outcome; overwrite historical evidence; merge on stale-SHA evidence; let throughput optimize correctness; let tool-definition quality masquerade as task success; or let a relationship candidate become an asserted fact.

**Owner boundaries:** CRG owns relationship evidence; adaptive-wait owns asynchronous control; evidence-led-monorepo-ops owns repository evidence discipline; ATES owns execution telemetry; TDQS owns tool-definition quality.