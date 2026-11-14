# DoE / MoneyBall — QUE Device Backend Comparison

**Proposal:** `que-device-validation` · Item QDV-006 / QDV-010  
**State:** design and candidate arms only; no runtime experiment claimed.

## Question

Which execution architecture yields the highest verified device-component validation value per total cost while preserving target fidelity, reproducibility, security and hardware acceptance?

## Treatments

| Arm | Description | Status |
|---|---|---|
| A — QUE-native | Existing registered workflows and runners; no new backend fleet. | Baseline candidate |
| B — QUE + specialists | QUE dispatches to capability-matched AVD, Termux container, QEMU, Waydroid or physical device. | Recommended architecture to test |
| C — dedicated fleet | Reusable, managed emulator/device fleet with versioned images, health and reset controls. | Costly alternative candidate |

A/B/C are strategy-level treatments. Backend family and profile version are additional factors. Do not confound a change in strategy with a change in test suite, source SHA, Android API, ABI or runner class.

## Experimental unit and blocking

Experimental unit: one module-lane × test-suite × target-SHA execution.

Block on:
- module lane and owning component;
- test class and seeded defect class;
- Android API / ABI / Termux version / CPU architecture;
- host runner class and acceleration availability;
- workload size and test fixture version.

Randomize execution order within feasible blocks. Repeat each treatment enough times to estimate flake rate and uncertainty. Pre-register sample size, stopping rule, missing-data treatment, exclusions and analysis before looking at comparative outcomes.

## Hard gates

These are non-compensatory:
1. target behavior and correctness are preserved;
2. security, isolation and privacy policy passes;
3. environment identity is reproducible;
4. evidence is complete and SHA-bound;
5. capability claims are supported by observed evidence;
6. cleanup/reset is successful;
7. hardware-dependent requirements receive physical-device acceptance.

A fast or cheap arm failing any hard gate is ineligible regardless of composite score.

## Outcomes

Primary:
- confirmed seeded/known defect detection rate;
- emulator/device disagreement rate;
- valid run rate and flake rate;
- evidence completeness and reproducibility.

Secondary:
- module capability coverage;
- false-positive/false-negative rate where ground truth exists;
- queue wait, startup, execution and total feedback latency (median/p95);
- cost per valid run and per confirmed defect detected;
- CPU, RAM, disk, concurrency and reset/recovery time;
- adapter/image maintenance burden.

## MoneyBall analysis

Publish raw values, denominators, missingness, uncertainty intervals and Pareto fronts first. The Pareto dimensions are:
- fidelity / defect detection;
- reliability / reproducibility;
- coverage;
- latency;
- cost;
- maintenance burden.

Only after baseline variance and owner priorities are observed should a weighted utility score be pre-registered. The weights must include rationale, sensitivity analysis and hard-gate constraints. Do not manufacture a winner from guessed weights.

A backend can be culled only with recorded evidence and rationale. A retained backend must have a defined module/test use case. Combination arms are admitted only when their interaction benefit exceeds their integration, security and maintenance cost.

## Required experiment record

Every executed observation reuses `docs/ops/corpus/EXPERIMENT.schema.json` and the canonical `docs/ops/EVIDENCE-ENVELOPE.schema.json`. One dispatched/executed run equals one observation. Each observation references:
- baseline SHA and candidate SHA;
- module lane, suite, cohort/block and treatment;
- tool profile ID, exact tool/image version and runtime fingerprint;
- QUE task/run/attempt identity;
- outcome, metrics, confidence and provenance;
- evidence artifact pointers and reset result.

## Admission boundary

This design does not itself admit or dispatch an experiment. The DoE family admission protocol and existing execution controller remain authoritative. QDV-010 stays queued until the cohort, design, resource budget, backend availability and evidence path are approved and pinned.
