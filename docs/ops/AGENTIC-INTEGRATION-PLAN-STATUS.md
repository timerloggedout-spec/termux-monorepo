# Agentic Integration Plan & Status

**Scope:** SHE + ATES/WTCV + Action→Effect + Historical Context Relationship corpus + Hex-compatible evidence + Docker/Codespaces + review orchestration.

**Primary branch:** `master`  
**Active integration PR:** #523 (`ops/automate-historical-backfill-ates-she`)  
**Current observed PR head at plan publication:** `dac711d43536f64d097aa2dc7375940f2361ade5`

## Operating loop

The repository uses the following evidence-first control loop for non-trivial automation:

`RECON → PLAN/MEASURE → IMPLEMENT/ACT → COMMIT → WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → CLASSIFY → RECORD → REPEAT`

A queued or in-progress workflow is **not** execution success. The four states below are independent:

- **COMMITTED:** the intended change exists at a known SHA.
- **EXECUTED:** the runtime actually ran the intended workflow/job.
- **VALIDATED:** checks/evidence establish the intended result.
- **PROMOTED:** the result was deliberately moved to the authoritative branch.

Failures and cancellations are observations. They are not automatically converted into retries merely to make the dashboard green.

## Current PR #523 evidence

At the most recent watch cycle, PR #523 was open, non-draft, mergeable, based on `master`, with head SHA `dac711d43536f64d097aa2dc7375940f2361ade5`.

The prior head `1b8cb650b303902a3eca1943e9f04428172beabf` produced a fresh Actions cohort. The observed terminal state was:

| Workflow | Run | Result |
|---|---:|---|
| Advisory GitHub Actions lint | 34932775403 | SUCCESS |
| DeepSeek CI – Agentic Automation | 34932775405 | CANCELLED before steps were exposed |
| context relationship validation | 34932775453 | SUCCESS |
| Workflow Surface Policy | 34932775480 | SUCCESS |
| Workflow Surface Evidence | 34932775514 | SUCCESS |
| Repository development evaluation | 34932775562 | SUCCESS |
| repo gate | 34932775483 | SUCCESS |
| Context Relationship + Lead/Lag Audit | 34932775482 | SUCCESS |
| Automation Documentation Continuous Refresh | 34932775440 | SUCCESS |
| termux smoke | 34932775586 | SUCCESS |
| ECC Tools comment-command ops | 34932775534 | SUCCESS |
| Audit Cycle — Single PR Feed-Forward | 34932775587 | SUCCESS |
| Gemini Dispatch (free-tier agentic) | 34932775730 | SUCCESS |
| Advisory CodeQL analysis | 34932775490 | SUCCESS |

The cancelled DeepSeek run had one job (`deepseek-agent`, job `104264298629`) and exposed no completed steps. Its log endpoint returned no retained blob. Therefore the correct classification is **CANCELLED / UNEXPLAINED FROM RETAINED JOB EVIDENCE**, not failure and not success.

## ATES status

ATES is already implemented at **Phase A**. It is not being deferred until some later “fancy” phase.

Phase A currently includes:

- pure network-free reducer;
- TCV and WTCV;
- retry/error penalty (RPI);
- action density;
- parallel yield;
- ATES;
- token processing velocity (TPV);
- context ingestion efficiency (CIE);
- tool delay;
- handoff latency;
- JSONL event schema;
- focused unit tests;
- explicit-complexity handling;
- structural complexity fallback;
- missing-evidence `null` behavior;
- visible Actions quality verification.

### Why another review layer?

The normal PR review is **not replaced** by ATES. Once Phase A exists, a later review/evidence cycle can attach ATES to the same cohort:

`PR REVIEW → CHECKS → ACTION→EFFECT → ATES/WTCV → LONGITUDINAL RECORD`

This is intentionally additive. ATES can reveal efficiency differences after correctness/evidence are established; it cannot declare an unvalidated change successful.

## Quality lane

`.github/workflows/agent-quality-lane.yml` now provides a dedicated check. It verifies:

- implementation and contract files exist;
- public telemetry surfaces have documentation;
- non-obvious formulas have explanatory source comments;
- `MIN_ATES_THRESHOLD` is absent;
- event schema parses as JSON;
- focused ATES tests pass;
- structural complexity and missing-evidence invariants remain covered.

This is a documentation/maintainability gate, not a crude comment-density metric.

## Historical corpus

The canonical context-relationship corpus remains **PARTIAL**. The last observed manifest reported `next_start_page = 2`, so historical continuation is not complete.

The successor workflow is designed to:

1. read the canonical manifest from current `master`;
2. resume from `next_start_page`;
3. process a bounded page/window;
4. verify page advancement and hashes;
5. commit only corpus deltas;
6. stop safely if `master` moves during the write.

A real Actions run is required before classifying the successor as EXECUTED. A branch commit containing the workflow is only COMMITTED.

## Hex evidence provenance

The known artifact from Actions run `34318469134` is real and internally consistent, but it is a GitHub Actions `upload-artifact` ZIP implementing the repository's `3l0.moneyball.v1` contract. It is **not evidence of a native Hex-generated ZIP**.

Known artifact facts:

- artifact: `hex-moneyball-evidence-34318469134-1.zip`;
- Actions artifact ID: `10090930230`;
- contract: `3l0.moneyball.v1`;
- records: `6`;
- validation: `VALIDATED`;
- raw content export: `false`;
- actual downloaded ZIP SHA-256: `48b066822822bf1995d51f550065cb2f912d7f07d9350953412e7050c1045883`.

Native Hex project import/use remains **UNVERIFIED / NOT ESTABLISHED** because the connected Hex surface reported a Team/Enterprise plan restriction and no live project was inspected.

## Environment strategy

Docker and Codespaces are related but intentionally distinct:

- Docker: reproducible automation substrate, CI execution, isolated tool/provider experiments, image-level reproducibility, environment fingerprints.
- Codespaces: interactive sandbox, development/reproduction surface, debugging, exploratory agent workflows.
- Shared environment metadata can support comparisons.
- Neither is the canonical evidence store.

## Planned phases

### Phase A — Measure **IMPLEMENTED**

Reducer + schema + fixtures + quality gate.

### Phase B — Emit **NEXT**

Eligible agent workflows emit sanitized JSONL receipts with run/attempt/SHA linkage.

### Phase C — Correlate

Join telemetry to GitHub Actions, PR/review, Action→Effect, corpus, and environment evidence. Re-run comparable PR review cohorts with ATES attached.

### Phase D — Experiment + reproduce

Compare Langfuse/Phoenix adapters over the same cohort; use Docker and Codespaces for their distinct experiment/reproduction purposes.

### Phase E — Manager evolution

Use validated quality/effectiveness + complexity-adjusted throughput to compare orchestration policies. Never optimize ATES alone.

## Explicit non-goals

- no speed-only merge gate;
- no synthetic zeros for missing evidence;
- no vendor source-of-truth replacement;
- no secret/PAT emission into telemetry or images;
- no automatic rerun solely to obtain green status;
- no assumption that queued means executed;
- no assumption that Docker and Codespaces are interchangeable;
- no claim of native Hex export without native provenance.

## Next evidence transitions

1. Wait/watch the new PR head's Actions cohort after the latest documentation/code commits.
2. Validate the dedicated quality lane and focused ATES tests.
3. Inspect any cancellation/failure rather than blindly retrying it.
4. Re-fetch PR SHA/mergeability and review state after checks settle.
5. If the PR is deliberately promoted, observe the resulting `master` workflow cohort.
6. Observe the scheduled historical backfill and record `next_start_page` advancement.
7. Repeat bounded continuation until the manifest explicitly reports completion.
