# CNS Integration Programme Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Integrate the repository's existing CNS organs through canonical ownership, shared identity, evidence-backed interfaces, and read-only health projections.

**Architecture:** Use one accepted proposal and sixteen independently trackable work items. Begin with the organ registry, map, and authority matrix; then integrate identity, CRG, Brain, Synaptic Bus, routing, scoring, and presentation through existing canonical owners. Existing stores, queues, routers, gates, and ledgers remain authoritative.

**Tech Stack:** GitHub Actions, Python, Rust, YAML/JSON Schema, Mermaid, Markdown, existing repository dashboard stack.

**Spec:** `docs/proposals/active/cns-integration/MANIFEST.md`

## Global constraints

- Follow `CLAUDE.md`, proposal lifecycle, dual gates, and `docs/proposals/AGENTIC-PERMISSIONS.md`.
- Target `master` through reviewed feature branches and PRs.
- Every PR and commit cites `Implements: CNS-<id>`.
- Reuse canonical organ schemas and records.
- Keep verified, derived, inferred, and candidate evidence distinct.
- Preserve provider, model, agent, role, and adapter identities.
- Treat dashboards and CNS registries as read-only projections.
- Require TDD for behavior changes and exact-head verification before completion.

## Review focus

- Duplicate native event delivery: consumers resolve idempotently to the same canonical event.
- Missing identity fields: projections retain explicit unknown status.
- Cross-SHA correlation: mismatched source revisions remain candidate or unresolved.
- Partial historical corpus: health and UI preserve partial coverage.
- Pending execution: queued and in-progress work remains pending until native terminal evidence arrives.

---

### Task 1: CNS-01 — Organ registry

**Files:** `docs/architecture/CNS-ORGAN-REGISTRY.yaml`, registry validation tests.  
**Interfaces:** Produces stable organ IDs, owners, canonical sources, status, responsibilities, and authority boundaries.

- [ ] Add schema/contract tests for unique IDs, required source paths, status vocabulary, and evidence class.
- [ ] Run focused tests and observe expected failures for malformed fixtures.
- [ ] Implement validation following existing repository schema patterns.
- [ ] Validate all registered paths against the repository tree.
- [ ] Run repo gate and Termux smoke; record baseline findings.
- [ ] Commit with `Implements: CNS-01`.

### Task 2: CNS-02 — Integration map

**Files:** `docs/architecture/CNS-INTEGRATION-MAP.mmd`, Mermaid validation tests.  
**Interfaces:** Consumes CNS-01 organ IDs and classifications.

- [ ] Test node/edge coverage and classification consistency.
- [ ] Run Mermaid renderer validation and observe expected failure for an invalid edge fixture.
- [ ] Implement map validation or repository-native rendering check.
- [ ] Confirm proposed edges remain visually and textually distinguishable.
- [ ] Commit with `Implements: CNS-02`.

### Task 3: CNS-03 — CRG reconciliation

**Files:** Existing CRG collector, manifest, backfill workflow, validation tests.  
**Interfaces:** Consumes canonical CRG schema and scope registry; produces fresh manifest and receipt.

- [ ] Add tests for continuation checkpoint, idempotency, source SHA binding, parser failure accounting, and candidate preservation.
- [ ] Run focused tests and observe expected failures.
- [ ] Continue bounded backfill from the current canonical checkpoint.
- [ ] Reconcile unresolved references and parser failures.
- [ ] Validate immutable snapshot lineage and artifact hashes.
- [ ] Record coverage and checkpoint eligibility from fresh evidence.
- [ ] Commit with `Implements: CNS-03`.

### Task 4: CNS-04 — Shared identity

**Files:** CNS event/identity contract, existing envelope schemas, adapter and contract tests.  
**Interfaces:** Consumes native identifiers; produces a read-only correlation projection.

- [ ] Add contract tests for multi-attempt tasks, provider/model separation, adapter identity, run attempts, missing values, and cross-SHA joins.
- [ ] Run tests and observe expected failures.
- [ ] Implement explicit mappings to existing native fields.
- [ ] Validate compatibility with Synaptic Bus and Orchestration Receipt contracts.
- [ ] Commit with `Implements: CNS-04`.

### Task 5: CNS-05 — Authority matrix

**Files:** `docs/architecture/CNS-AUTHORITY-MATRIX.md`, governance validation.  
**Interfaces:** Consumes organ registry; produces canonical owner and permission references.

- [ ] Add tests for unique mutable-domain owner and required source references.
- [ ] Run tests and observe expected failures for duplicate owners.
- [ ] Implement matrix validation and link current governance records.
- [ ] Review security-sensitive ownership with repository permissions.
- [ ] Commit with `Implements: CNS-05`.

### Task 6: CNS-06 — Brain host integration

**Files:** Existing Brain host, bridge, typed extension, and integration tests.  
**Interfaces:** Consumes CNS identity mapping and Brain kernel contracts.

- [ ] Add a failing host-route test for one bounded specialist invocation.
- [ ] Verify RED against the current unwired host path.
- [ ] Implement the smallest bridge using the canonical host.
- [ ] Verify policy delegation, attempt lineage, receipt, and degraded-state handling.
- [ ] Run Rust and repository test suites.
- [ ] Commit with `Implements: CNS-06`.

### Task 7: CNS-07 — Synaptic Bus

**Files:** PR #5637 contract, adapter, compatibility tests, and existing event-family adapters.  
**Interfaces:** Consumes CNS-04 identity projection; produces canonical event references.

- [ ] Add failing idempotency and event-owner compatibility tests.
- [ ] Verify RED against the existing adapter behavior.
- [ ] Complete envelope compatibility and projection adapter.
- [ ] Verify privacy, append-only semantics, schema versioning, and exact-head checks.
- [ ] Commit with `Implements: CNS-07`.

### Task 8: CNS-08 — ORBIT / SHIELD

**Files:** PR #5544 arbitration/context admission, Router boundary, observe-only tests.  
**Interfaces:** Consumes CNS-04 identity projection and Router eligibility evidence.

- [ ] Add failing invocation-boundary observation tests.
- [ ] Verify RED against the current routing path.
- [ ] Integrate observe-only SELECT/DEFER/VETO evidence.
- [ ] Verify unchanged dispatch behavior during observation.
- [ ] Run exact-head tests and record comparison evidence.
- [ ] Commit with `Implements: CNS-08`.

### Task 9: CNS-09 — 3L0 intake

**Files:** 3L0 intake, collector, feed, schema, and tests.  
**Interfaces:** Consumes invocation receipts and confirmed task outcomes.

- [ ] Add failing attribution and repeated-outcome tests.
- [ ] Verify RED against current intake coverage.
- [ ] Implement canonical receipt mapping and append-only intake.
- [ ] Verify endpoint instance, actor, provider, model, run, and outcome attribution.
- [ ] Recompute scores from confirmed evidence and retain cold-start distinctions.
- [ ] Commit with `Implements: CNS-09`.

### Task 10: CNS-10 — Orchestration DoE/MVT

**Files:** Existing experiment schemas, treatment identity, manager tournament pipeline, tests.  
**Interfaces:** Consumes CNS-04 identity and CNS-09 outcomes.

- [ ] Add failing cohort comparability and attribution tests.
- [ ] Verify RED against current experiment input.
- [ ] Implement one bounded policy comparison using existing DoE/MVT.
- [ ] Record treatment, control, manager, provider, model, context, and catalog snapshot.
- [ ] Evaluate correctness, integration time, retries, conflict, context efficiency, and intervention.
- [ ] Commit with `Implements: CNS-10`.

### Task 11: CNS-11 — Single-writer coordination

**Files:** Existing GitHub/GitLab reconciliation and corrective-write adapters, lease contract, concurrency tests.  
**Interfaces:** Consumes repository/PR/revision identity.

- [ ] Add failing concurrent-owner and stale-lease recovery tests.
- [ ] Verify RED against current cross-platform coordination.
- [ ] Implement the smallest lease/write gate at the mutation boundary.
- [ ] Verify owner expiry, revision fencing, and audit receipts.
- [ ] Run GitHub/GitLab reconciliation tests.
- [ ] Commit with `Implements: CNS-11`.

### Task 12: CNS-12 — SHE CNS overview

**Files:** Existing SHE reducers, snapshot schema/publisher, read-only UI, tests.  
**Interfaces:** Consumes organ registry, health model, CRG, telemetry, 3L0, MoneyBall, and DoE projections.

- [ ] Add failing provenance, freshness, partial-state, and source-SHA tests.
- [ ] Verify RED against the existing snapshot pipeline.
- [ ] Implement deterministic CNS reducer and snapshot projection.
- [ ] Implement accessible read-only organ overview.
- [ ] Verify snapshot lineage and source links.
- [ ] Commit with `Implements: CNS-12`.

### Task 13: CNS-13 — Historical Corpus Explorer

**Files:** Existing `apps/historical-corpus-explorer/`, publisher, temporal validator, and tests.  
**Interfaces:** Consumes CRG manifest and immutable snapshots.

- [ ] Add failing coverage contradiction and temporal gating tests.
- [ ] Verify RED against the existing Explorer.
- [ ] Complete manifest/schema/count and lineage reconciliation.
- [ ] Verify accessible table fallback and bounded exploration.
- [ ] Deploy using the existing approved dashboard path and capture deployment evidence.
- [ ] Commit with `Implements: CNS-13`.

### Task 14: CNS-14 — Adaptive wait-loop skill

**Files:** Existing adaptive feedback cycle skill, skill inventory, fixtures/lint tests.  
**Interfaces:** Consumes uploaded Loopy reference and repository adaptive-wait contract.

- [ ] Compare source skill and repository skill line by line.
- [ ] Add failing fixtures for terminal-state classification and verification-before-repeat.
- [ ] Integrate the six-step micro-loop and nine route labels into adaptive-wait; keep terminal states and receipts owned by adaptive-wait, with the twelve-step macro-cycle owned by adaptive-feedback-cycle.
- [ ] Update inventory and usage references.
- [ ] Validate lint and skill contract tests.
- [ ] Commit with `Implements: CNS-14`.

### Task 15: CNS-15 — Jules workflows

**Files:** Existing Jules issue/PR/review workflows, action pins, tests, skill documentation.  
**Interfaces:** Consumes uploaded Jules workflow reference and current repository permissions.

- [ ] Add failing trigger, input, permission, and invocation-attribution tests.
- [ ] Verify RED against current workflow definitions.
- [ ] Reconcile action versions and inputs with authoritative action contracts.
- [ ] Validate secret handling, prompt bounds, reproducibility, and review handoff.
- [ ] Run workflow contract tests and exact-head checks.
- [ ] Commit with `Implements: CNS-15`.

### Task 16: CNS-16 — Notation enforcement

**Files:** Existing notation registry, PR #5635, Vale/markdownlint configuration, CI fixtures.  
**Interfaces:** Consumes current repository positive-form and operator notation rules.

- [ ] Add failing fixtures for directive form, operator semantics, code blocks, and quoted source.
- [ ] Verify RED against current lint behavior.
- [ ] Reconcile the registry and implement scoped lint rules.
- [ ] Document exceptions and false-positive handling.
- [ ] Run focused lint tests and repository gates.
- [ ] Commit with `Implements: CNS-16`.

## Integration order and dependency notes

- CNS-01 and CNS-05 establish the registry and authority boundaries.
- CNS-02 consumes CNS-01.
- CNS-03 can proceed independently using canonical CRG checkpoints.
- CNS-04 maps existing native identifiers and is a prerequisite for runtime correlation in CNS-06 through CNS-12.
- CNS-07 and CNS-08 extend existing open PRs; preserve their original owners and review history.
- CNS-09 consumes invocation evidence; CNS-10 consumes CNS-09 confirmed outcomes.
- CNS-11 is a separate mutation-boundary safety track.
- CNS-12 consumes canonical projections; CNS-13 remains a CRG-specific read-only surface.
- CNS-14 through CNS-16 are skill/governance consolidation tracks.

## Verification commands

- `python3 scripts/ci/repo_gate.py`
- `python3 scripts/ci/termux_smoke.py`
- Focused test commands recorded in each implementation brief.
- Exact-head GitHub Actions checks for every PR.
- Runtime receipt verification for each operational integration.

## Completion rule

A CNS item is complete only when its implementation is merged through the governed branch process, its acceptance tests pass, and its required runtime or artifact evidence is linked from the item. Documentation and issue creation establish tracking, not implementation completion.


## Current evidence gates

- CNS-03 uses the existing operator-dispatched CRG backfill workflow. The current connector supports run inspection and reruns; workflow dispatch remains an operator action through the repository's approved workflow interface.
- CNS-06 runtime wiring remains gated by QDesk Brain RFP #5501, its Delphi recheck, and verified QUE/QDesk host ownership. Source reconciliation and read-only bridge design proceed within the existing scope.
- CNS-09 reuses `ops/3l0/intake.jsonl` and its existing fan-out/attribution pipeline. The current intake has 41 records and zero confirmed outcomes; the committed 3L0 feed is stale. CNS-09 prioritizes attribution and feed reconciliation before any score movement.
- CNS-10 consumes the existing DoE/MVT experiment plane and PCDOE-008 prioritization work. The first treatment compares one bounded manager policy against the incumbent on a pinned cohort.
- CNS-11 separates GitHub Actions concurrency from external provider write enforcement. A local concurrency group establishes only the internal workflow coverage that its evidence proves.
- CNS-12 reuses SHE reducers, snapshot metadata, and Tribute dashboard surfaces. CNS-13 remains the CRG-15 Explorer publication/deployment follow-through.
- CNS-15 uses `docs/ops/JULES-INTEGRATION-RECONCILIATION.md` and the existing workflow tests as its source and compatibility guard.
- CNS-16 consumes PR #5635 and the canonical notation registry.

