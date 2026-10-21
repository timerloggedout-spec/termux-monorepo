# Blind Agent Evaluation Skill

## Purpose

Use blinded or partially blinded evaluation when provider/model identity could bias selection or review and identity is not required for safe execution. This is a **double-blind-style engineering control**, not a guarantee of perfect statistical blindness.

## Procedure

1. Define the task, success criteria, factors, cohorts, and evidence requirements.
2. Assign opaque treatment IDs before evaluation when feasible.
3. Remove unnecessary provider/model/reputation metadata from evaluator-visible material.
4. Execute treatments while preserving secure provenance.
5. Freeze evidence before unblinding when practical.
6. Evaluate correctness first; score completeness, regressions, warnings, severity, and other task metrics separately.
7. Record uncertainty, missingness, failures, cooldowns, and inference/leakage of identity.
8. Unblind only after evaluation, or document operational/safety exceptions.
9. Compare results across treatments and replicate promising findings.
10. Feed verified findings into MoneyBall/3L0 and BIUDL.

## Anti-bias rules

- Do not let provider/model reputation substitute for evidence.
- Do not call a trial double-blind when identity is readily inferable.
- Do not erase attribution: protected provenance must survive blinding.
- Do not optimize latency ahead of correctness.
- Do not treat HTTP/workflow success as task success.
- Do not silently change prompts, cohorts, or scoring after seeing treatment identity.

## Multi-agent coordination

Scout proposes candidate treatments. Managers choose experiments under the applicable assignment policy. Evaluators score blinded evidence. Telemetry maintains runtime lineage. MoneyBall/3L0 ranks treatments after the evaluation boundary. Synthesis updates the next BIUDL baseline.

## Escalation

If blinding conflicts with safety, debugging, quota/cooldown intervention, or required operational metadata, preserve the necessary visibility and record the exception. Prefer **partial blindness with explicit provenance** over unsafe or unverifiable execution.

## Evidence lineage

`experiment → opaque treatment → execution → evidence → evaluator result → unblind → provider/model attribution → ranking → synthesis`.

## Continuous improvement

Every use of this skill should be eligible for retrospective critique: leakage discovered, evaluator disagreement, selection imbalance, replication outcome, and regression findings become inputs to the next revision of this skill.


## Pairwise tournament and judge-calibration extension

When comparing System One candidates, use this additional contract:

1. **Freeze the evaluation unit.** A row is keyed by evaluation ID, dataset version, question ID, task family, opaque treatment ID, source SHA, adapter/runtime version, and run ID + run attempt.
2. **Separate outcome classes.** Distinguish correct/incorrect, abstention, invalid schema, timeout, provider throttling, transport error, cancellation, and missing observation. Never map infrastructure errors to incorrect model answers by default.
3. **Score ground truth first.** Use deterministic exact/structured scoring where valid; otherwise use a versioned rubric and independently reviewed adjudication. Peer preference is a secondary metric.
4. **Blind pairwise judging.** Randomize A/B order, include reversed duplicate pairs, preserve each judge's raw verdict and rubric dimension, and flag identity leakage.
5. **Calibrate judges.** Include known control pairs and human/adjudicated gold cases. Report agreement, pairwise consistency, position bias, self-preference, judge variance, abstention, and missingness. A judge failing the declared calibration threshold is diagnostic only.
6. **Quantify uncertainty.** Report paired confidence intervals or bootstrap intervals over cases. Keep per-task and per-risk slices; do not publish a global winner when samples are too small or materially non-comparable.
7. **Report multi-objective results.** Correctness, safety, schema validity, abstention/coverage, regression severity, p50/p95/p99 latency, throughput, cost and resource use stay separate. A composite score is allowed only with a versioned formula and a sensitivity report.
8. **Preserve receipts.** Retain sanitized JSONL with immutable source/run IDs, config/prompt/schema hashes, score schema version, candidate output hashes, metric definitions and artifact digest. Raw sensitive prompts/completions do not enter shared telemetry by default.
9. **Require independent promotion evidence.** The candidate cannot self-certify. Promotion needs objective task evidence, calibrated judging where used, safety/regression checks, minimum slice coverage and a reproducible rerun on the candidate SHA.
10. **Close the loop.** Store result IDs in the canonical evidence envelope/MoneyBall contract and link the resulting claim to issue → PR → commit → workflow → artifact. Update the skill only after reviewing observed disagreements, leakage, replication and regression.

### Metric interpretation safeguards

- Pairwise win rate is preference, not correctness.
- Exact match is only valid when the task output has canonical semantics.
- Abstention must be measured as both a count/rate and a risk-coverage trade-off; don't reward blanket abstention.
- Latency and throughput are valid only under declared comparable load/hardware/cache conditions.
- A successful workflow or reachable endpoint is not a successful task.
- Do not set an ATES-only merge gate: quality and evidence dominate throughput.
- Keep test/training/validation/held-out slices distinct; never tune against the final held-out results.
