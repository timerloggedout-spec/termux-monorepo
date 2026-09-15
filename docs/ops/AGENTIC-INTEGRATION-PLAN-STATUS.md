# Agentic Integration Plan & Status

**Scope:** SHE + ATES/WTCV + Action→Effect + Historical Context Relationship corpus + Hex-compatible evidence + Docker/Codespaces + review orchestration.

**Primary branch:** `master`  
**Active integration PR:** #523 (`ops/automate-historical-backfill-ates-she`)

## Operating loop

The repository uses this evidence-first control loop for non-trivial automation:

`RECON → PLAN/MEASURE → IMPLEMENT/ACT → COMMIT → WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → CLASSIFY → RECORD → REPEAT`

WAIT is now an **active-work state**, not idle sleep. While one cohort is waiting, independent non-conflicting work continues; the watched cohort is re-checked at the next evidence boundary. Every wait cycle records its last observed state and next observation point.

`QUEUED` and `IN_PROGRESS` are runtime states, not success. `COMMITTED`, `EXECUTED`, `VALIDATED`, and `PROMOTED` remain independent evidence states.

## Why the corpus is still on page 2

This is currently a **promotion/runtime sequencing issue, not an unexplained collector stall**.

The authoritative `master` manifest is still the older corpus snapshot from August 19 and explicitly reports `start_page = 1` and `next_start_page = 2`. It also still carries the legacy `default_branch = master-staging`. cite-not-applicable

The new continuation writer and its legacy-branch migration compatibility exist on PR #523, but they are not authoritative until #523 is deliberately promoted. Therefore no honest claim can be made that page 2 has executed on `master` yet.

After promotion, the expected sequence is:

1. scheduled/dispatch run admits against current `master`;
2. canonical manifest is read;
3. the bounded continuation starts at page `2`;
4. the builder emits a new manifest/report;
5. validation requires page advancement or `null` completion;
6. the corpus delta is committed to `master` only after validation;
7. the watcher re-fetches the resulting SHA and manifest;
8. the next scheduled run resumes from the newly observed `next_start_page`.

A completed run that leaves `next_start_page` unchanged is now classified as a **pagination stall**, not silently accepted.

## Runtime stall detection

`.github/workflows/agent-runtime-stall-watch.yml` is now an observer-only watchdog. It periodically records queued and in-progress runs, immutable SHA/ref identity, age, and stall classification. It never reruns, cancels, merges, or mutates candidate work.

Current diagnostic classes include:

- admission stall;
- queue stall;
- execution/heartbeat stall;
- effect stall;
- pagination stall;
- routing loop.

The watchdog's thresholds are diagnostic signals, not automatic retry authorization. A retry requires a diagnosis/policy and receives a new event identity while preserving the original stall observation.

## Current phase state

### Phase A — Measure **IMPLEMENTED / VALIDATED**

Pure ATES/WTCV reducer, sanitized event schema, explicit and structural complexity, missing-evidence invariants, focused tests, and a visible Actions quality gate.

### Phase B — Emit **STARTED**

The runtime emission contract is defined: sanitized JSONL, immutable run/attempt/SHA linkage, and environment fingerprint fields where available. The next implementation increment wires eligible agent workflows to emit these receipts alongside their existing artifacts.

### Phase C — Correlate **STARTED / CONTRACT DEFINED**

The correlation target is now explicit: Actions run/attempt + SHA + PR/review + Action→Effect + corpus observation + environment evidence. ATES is attached after correctness/evidence, not used to replace review.

### Phase D — Experiment + Reproduce **STARTED / ADAPTER PLAN DEFINED**

Langfuse and Phoenix are parallel adapters over the same bounded cohort and canonical event contract. Docker is the reproducible execution substrate; Codespaces is the interactive sandbox/reproduction surface. They are not collapsed into “parity.”

### Phase E — Manager evolution **STARTED / DECISION CONTRACT DEFINED**

Manager policies will eventually compete using validated outcome/effectiveness plus complexity-adjusted throughput, retries, conflicts, attribution confidence, human intervention, and cost. ATES alone is never the objective function.

## ATES is core, not “fancy”

ATES is already part of Phase A and therefore part of the core architecture. The later review layer is additive:

`PR REVIEW → CHECKS → ACTION→EFFECT → ATES/WTCV → LONGITUDINAL RECORD`

The purpose of repeating the review/evidence cycle with ATES attached is to learn whether an orchestration policy is **more effective at comparable complexity**, not merely faster.

## Quality lane

`.github/workflows/agent-quality-lane.yml` verifies implementation/contract presence, documentation, explanatory source comments for non-obvious formulas, absence of a speed-only merge threshold, schema validity, focused tests, structural complexity, and missing-evidence invariants.

The new runtime watchdog is deliberately observer-only so the quality lane does not become a hidden control plane.

## Environment strategy

Docker and Codespaces are related but intentionally distinct:

- **Docker:** reproducible automation substrate, CI execution, isolated provider/tool experiments, image-level reproducibility, environment fingerprints.
- **Codespaces:** interactive sandbox, development/reproduction surface, debugging, exploratory agent workflows, and issue reproduction.
- Shared environment metadata can support comparisons.
- Neither is the canonical evidence store.

## Hex / Wolfram status

The existing Hex-compatible Moneyball evidence lane remains implemented; native Hex project import/use remains unverified because the connected Hex surface reported a Team/Enterprise restriction.

Wolfram API-key generation is currently blocked by the observed Developer Portal HTTP 500. Until the portal recovers, comparative computation can proceed through the connected Wolfram Language/Alpha tools where available, plus local deterministic implementations for the same formulas. The local implementation remains the reproducibility baseline; Wolfram is an optional independent comparator, not a single point of failure.

## Promotion boundary

PR #523 remains deliberately unpromoted until the current-head checks/review evidence are re-fetched and the promotion decision is explicit. Once promoted, the next evidence target is the actual `master` historical-backfill run—not a declaration based solely on the presence of the workflow file.
