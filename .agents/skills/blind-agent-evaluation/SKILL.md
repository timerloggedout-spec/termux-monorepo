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
