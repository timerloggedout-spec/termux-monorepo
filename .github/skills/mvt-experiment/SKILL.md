# MVT Experiment Skill

## Purpose
Run controlled minimum-viable tests across branches, tags, and immutable commit SHAs without rewriting history.

## Contract
1. Resolve every ref to an immutable commit SHA before comparison.
2. Record experiment ID, baseline SHA, candidate SHA, merge-base, suite, timestamps, changed paths, and outcome.
3. Keep baseline and candidate immutable during measurement.
4. Compare like-for-like suites and preserve raw evidence.
5. A failed or missing observation is not a pass.
6. Provider/deployment failures are classified separately from repository correctness.
7. Promotion is a separate reviewed operation.
8. Never discard a superseded experiment without preserving its provenance.

## Loop
RECON -> SELECT -> RESOLVE -> MEASURE -> WAIT -> VALIDATE -> RE-FETCH -> COMPARE -> CLASSIFY -> REPEAT.

## Adapters
Forensics/Restore, fragment matching, reverse-pointer mapping, Chrono/time-loop analysis, notation taxonomy, workflow reliability, GitHub Actions, Linear, Notion, Hex, and Vercel may consume this contract. Adapters must emit the same evidence fields and must not mutate experiment refs.


## Canonical evidence and failure semantics

- The authoritative output contract is `docs/ops/corpus/EXPERIMENT.schema.json` (schema_version `1.0`). Do not emit private adapter schemas such as `agent-mvt-v1` as the canonical experiment record.
- Resolve baseline and candidate to immutable 40-hex commit SHAs before comparison. Never substitute a branch name or mutable ref in the canonical SHA fields.
- Execute the same selected suite independently against both detached refs. Record both exit codes; a missing exit code is a failed/incomplete observation, never a pass.
- Terminal record status is `passed` only when both suites exit zero, `failed` when either fails or a terminal result is missing, and `observed` for metadata-only comparison. A pre-resolution failure is preserved in a separate explicitly non-canonical failure envelope; it must not invent SHAs.
- Emit evidence under an unconditional/always path and upload it for success, failure, cancellation, and partial execution. Workflow success is not equivalent to experiment success.
- Keep failed stage, failure reason, run identity, attempt, and artifact URL in the evidence. Promotion remains separate and reviewed.
- Validate every canonical record against the checked-in JSON Schema before upload. Schema validation failure is itself a failed evidence-emission stage.

## Team MVT comparability

- A/B are the only same-task primary comparison arms in the current five-lane matrix.
- C/D/E are adversarial, integration-manager, and provider-umbrella diagnostic lanes. Preserve their evidence, but do not pool them with A/B or use them to estimate the same treatment effect.
- The GitHub matrix does not guarantee dispatch order. Record sequence control as uncontrolled; do not infer a randomized or counterbalanced sequence from a computed slot.
- Manager policy must be an explicit input/default, not derived from wall-clock minute.