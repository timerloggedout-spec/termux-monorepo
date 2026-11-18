# ADE-SYNAPSE Evolution Roadmap

This roadmap is a proposal. A stage advances only when its acceptance evidence exists.

## Stage 0 — Map the anatomy (this change)

**Goal:** establish a shared vocabulary and machine-readable registry.

Deliverables:
- region/network registry with explicit status and evidence paths;
- architecture model and interaction contracts;
- canonical Mermaid diagram;
- separate research, proposal, and experiment lanes.

Exit criteria:
- every mapping has a status;
- every existing mapping has repository evidence;
- proposed functions are not described as shipped;
- diagram and registry agree.

## Stage 1 — Instrument the synapses

**Goal:** make subsystem boundaries observable without adding another competing telemetry stack.

Candidate work:
- standard observation, context, action, and outcome envelopes;
- metadata-only Synaptic Bus v1 envelope, typed event taxonomy, and canonical-record compatibility matrix (contract and pure orchestration-receipt projection adapter implemented; no runtime publisher/consumer);
- correlation across task, manager, provider, model, adapter, workflow run/attempt, and source SHA;
- explicit event taxonomy for handoffs, attention shifts, conflicts, interruptions, and policy decisions;
- privacy and schema-closure tests.

Exit criteria:
- events are attributable and reproducible;
- schema and positive/negative fixtures pass Draft 2020-12 validation in CI;
- source adapters project existing canonical records without duplicating domain payloads (first orchestration-receipt adapter has focused tests);
- append-only consumers deduplicate by stable event ID;
- missing values remain null/unknown;
- no prompt, completion, secret, or arbitrary tool payload leakage;
- existing ATES/3L0/SHE evidence remains the canonical measurement base.

## Stage 2 — Build attention control

**Goal:** route attention, not just models.

Candidate work:
- severity and salience model for new issues, failed checks, stale runs, provider outages, and security signals;
- subscriptions with freshness windows and attention budgets;
- interrupt policy with deduplication, suppression, escalation, and expiry;
- distinguish scheduled observation from urgent interruption.

Exit criteria:
- measured missed-event and false-alert rates;
- no alert storms from duplicate events;
- critical events interrupt low-priority work only under explicit policy.

## Stage 3 — Strengthen episodic and semantic memory

**Goal:** make context retrieval useful, bounded, and provenance-aware.

Candidate work:
- context graph freshness and confidence;
- semantic notation/concept registry with aliases and deprecation;
- retrieval evaluation using known-answer fixtures;
- retention and consolidation policies that preserve source links.

Exit criteria:
- verified and candidate edges remain distinct;
- retrieval quality measured against fixtures;
- stale/partial corpus state visible;
- no silent deletion or authority inheritance from memory.

## Stage 4 — Introduce adaptive coordination

**Goal:** improve manager decisions through controlled comparison.

Candidate work:
- comparable cohorts and manager-policy tournaments;
- budget-aware parallelism and escalation;
- policy decision receipts including rejected alternatives;
- reward function constrained by correctness, safety, and acceptance.

Exit criteria:
- no single throughput metric can win;
- quality and acceptance remain primary;
- experiment identity preserves run/attempt, SHA, cohort, manager, route, and role;
- policy changes are reversible and explicitly promoted.

## Stage 5 — Consolidation and plasticity

**Goal:** retain useful lessons and decay noise safely.

Candidate work:
- periodic deduplication of observations;
- deterministic summaries with source pointers and confidence;
- stale knowledge marking and expiry;
- reversible policy adaptation with rollback checkpoints.

Exit criteria:
- every summary traces to source evidence;
- no loss of canonical history;
- reproducible before/after retrieval benchmarks;
- policy updates can be rolled back.

## Stage 6 — Multi-environment resilience

**Goal:** maintain function across Termux, GitHub Actions, containers, and interactive development surfaces.

Candidate work:
- liveness/readiness and degraded-mode contracts;
- environment fingerprinting;
- durable asynchronous wait/watch state;
- recovery receipts for interrupted runs.

Exit criteria:
- environment failures are distinguishable from model/provider/orchestration/code failures;
- no false claim that a queued job executed;
- bounded resource use on Termux.

## Permanent non-goals

- claiming consciousness, sentience, emotions, or biological equivalence;
- unrestricted self-modifying production code;
- autonomous credential or permission changes;
- optimizing activity volume instead of accepted outcomes;
- hiding failed, cancelled, stale, or incomplete evidence;
- allowing model output or retrieved text to override operator authority.

## Prioritization rule

Prefer the next capability that closes the largest evidence-backed gap at the lowest integration risk. Do not build a new subsystem when an existing contract or workflow can be extended safely.
