# Acceptance and Verification — Simulation Intelligence Plane

**Contract:** SIP-ACCEPT-001  
**State:** proposed; no live-engine acceptance claimed.

## Gate 0 — source, license and dependency census

- [ ] Exact MiroFish upstream commit, release, LICENSE and dependency licenses recorded.
- [ ] Refactoring fork commit and architectural delta recorded.
- [ ] CAMEL-AI OASIS release/tag, supported Python/runtime matrix, LICENSE and dependency lock recorded.
- [ ] Mesa and deterministic-baseline versions and license recorded.
- [ ] Model/data terms and redistribution constraints reviewed.
- [ ] No AGPL-derived code copied into this repository before explicit review.

Pass condition: immutable source URLs/SHAs, retrieval date, license evidence and dependency inventory are attached.

## Gate 1 — contract and offline baseline

- [ ] Scenario and Experiment JSON Schemas reject unknown fields and unsupported versions.
- [ ] Evidence references require immutable IDs and content digests.
- [ ] Persona schema distinguishes grounded attributes from generated assumptions.
- [ ] Run manifest requires code, data, graph, engine, adapter, prompt/config and seed identity.
- [ ] Simulation overlay schema cannot be mistaken for source graph evidence.
- [ ] Lifecycle state machine rejects illegal transitions.
- [ ] Duplicate and out-of-order events are idempotently reconciled.
- [ ] Fake engine executes without network, credentials or model calls.
- [ ] Deterministic fixture suite covers success, failure, cancellation, retry and finalization.
- [ ] No secret, raw prompt or private completion content appears in logs or artifacts.

Pass condition: all contract tests pass offline on one immutable SHA.

## Gate 2 — adapter conformance

- [ ] OASIS capability report is explicit and version-pinned.
- [ ] prepare/start/observe/stop/finalize/health map correctly or unsupported actions are explicit.
- [ ] OASIS environment reset/step/close behavior is tested.
- [ ] DB and event persistence are verified.
- [ ] Multi-platform completion and process liveness are separately observed.
- [ ] Adapter reports provider/model IDs and actual usage when available.
- [ ] Budget and concurrency limits fail closed.
- [ ] No second scheduler, queue, event bus, experiment registry or graph source is introduced.

Pass condition: adapter contract conformance against pinned OASIS without enabling public social actions.

## Gate 3 — sandbox pilot

- [ ] Owner-approved data cohort and purpose.
- [ ] Explicit agent/step/token/cost/time ceilings.
- [ ] Isolated local/sandbox environment.
- [ ] No real social-platform writes or external messaging.
- [ ] Run manifest and lifecycle receipt complete.
- [ ] Partial artifacts preserved after injected failure.
- [ ] Stop/finalize cleanup succeeds and leaves no orphan process.
- [ ] Human reviewer can reproduce or explain all deviations.

Pass condition: one bounded pilot with complete evidence and zero unauthorized side effects.

## Gate 4 — DoE comparison

- [ ] Frozen scenario, evidence cohort, graph snapshot and evaluator.
- [ ] At least two engines/policies and a deterministic baseline.
- [ ] Paired seed plan and declared randomization method.
- [ ] One experiment observation per executed run in the existing DoE family.
- [ ] Factor levels and exclusions recorded before execution.
- [ ] Primary outcomes pre-registered; secondary metrics separated.
- [ ] Missing/failed runs retained as failures or missingness, not silently dropped.
- [ ] Statistical uncertainty and limitations reported.
- [ ] Token/cost/latency normalized to comparable workload units.

Pass condition: reproducible paired comparison; no post-hoc selection of only favorable runs.

## Gate 5 — ATES / CEEL integration

- [ ] Trace ID and span hierarchy map to the existing ATES trace schema.
- [ ] Deterministic checks precede qualitative judging.
- [ ] Judge score cannot rescue deterministic failure.
- [ ] Normalized lifecycle events conform to CEEL integration-event schema.
- [ ] Event IDs/idempotency keys stable under replay.
- [ ] No raw prompt/completion/secret fields in canonical telemetry.
- [ ] Workflow execution success is not represented as scientific validity.
- [ ] Dashboard feeds are source-linked projections only.

Pass condition: exact-head repo-gate and Termux smoke (where available) on the same immutable SHA, with artifact references.

## Gate 6 — independent review and promotion

- [ ] Security/privacy review complete.
- [ ] License review complete.
- [ ] Cost/resource review complete.
- [ ] Independent scientific/technical review complete.
- [ ] Limitations and failure modes documented.
- [ ] Promotion decision recorded by authorized owner.
- [ ] Explicit confirmation that QUE, production routing and factual corpus remain unchanged unless a separate approved change exists.

Pass condition: explicit review and promotion receipt. PR merge alone is not promotion.

## Adversarial cases

1. A persona has no evidence reference: reject or mark unsupported; never fabricate provenance.
2. A simulated edge resembles an existing factual edge: retain it only in the simulation overlay.
3. A subprocess remains alive after all agents emit completion: mark engine-complete/process-open; do not claim running or finalized incorrectly.
4. One platform ends while another continues: overall run remains active.
5. Duplicate completion event arrives: no duplicate run or DoE observation.
6. Events arrive out of order: reconcile by event identity/time/version; preserve history.
7. Model returns malformed or oversized output: reject safely; retain bounded error metadata.
8. Resource budget is exceeded: stop/fail closed and preserve partial artifacts.
9. OASIS dependency is unavailable: offline fake engine remains testable; do not silently fall back to live provider.
10. Model provider returns a different actual model: record actual identity and mark configuration drift.
11. Qualitative judge claims success after deterministic invariant failure: final verdict remains deterministic failure.
12. Agent-generated report claims factual certainty: report renderer preserves claim class and provenance warning.
13. Prompt injection appears in a source document: treat as untrusted content, never as runtime instruction.
14. A cancelled run receives a late event: append late observation; do not rewrite terminal history.
15. A recovery process sees a stale RUNNING record but no live process: reconcile to failed/recovery-required; do not infer successful completion.
