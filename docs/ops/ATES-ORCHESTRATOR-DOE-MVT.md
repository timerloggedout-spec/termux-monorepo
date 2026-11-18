# ATES Orchestrator DoE / MVT Harness

## MVT
The minimum viable test cohort covers seven hard invariants: abstention availability, wrong-commit penalty, required-fragment preservation, distractor isolation, deterministic execution failure, isolated SPAWN behavior, and actor/critic private-context isolation.

## DoE
An experiment arm varies declared factors while task contract hash, environment fingerprint, benchmark version, and deterministic scorer remain fixed.

First factorial slice:
- routing: single | delegated
- actor_critic: off | on
- abstention: required
- spawn: isolated
- judge: off | inconclusive-only

Primary outcomes:
- deterministic pass rate
- boundary leakage rate
- required-fragment omission rate
- deterministic execution success rate

Secondary outcomes:
- net benchmark score
- wrong-commit count
- retry/error rate
- ATES/WTCV
- parallel yield
- time-to-integration
- human intervention
- attribution confidence

Canonical row identity is cohort × task × arm × repetition. Each row retains task fingerprint, environment fingerprint, benchmark version, arm-factor hash, trace id, deterministic verdict, ATES metrics, and optional judge score.

DSPy remains a consideration/optimization lane. Optimizer artifacts do not silently mutate production routing weights and remain subject to the existing dual-gate promotion path.

Failed experiments remain evidence and are not automatically rerun merely to improve dashboards.

## FCE as a secondary outcome

The ATES/MVT harness may emit an fce_observation_id reference for a completed task. The canonical FCE record is defined by docs/ops/FLYWHEEL-COMPOUNDING-EFFICIENCY.schema.json; ATES retains its own event/run identity and existing throughput measures. FCE is a secondary outcome beside deterministic pass rate, boundary leakage, retries, ATES/WTCV, integration time, human intervention, and attribution confidence. It is never a standalone acceptance or promotion gate.

DoE must freeze the normalization basis and matched baseline before execution. The campaign remains defined-but-not-run until its own admission and run evidence exist.
