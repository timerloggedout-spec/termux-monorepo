<!-- Local docs mirror. Canonical policy: .agents/skills/evidence-led-monorepo-ops/SKILL.md -->

# Evidence-Led Monorepo Operations — operational mirror

**Canonical:** .agents/skills/evidence-led-monorepo-ops/SKILL.md

## Loop

RECON -> CLASSIFY -> PLAN -> ACT -> WAIT -> VALIDATE -> RE-FETCH -> RECORD -> REPEAT

Goal: verified repository outcome, not a green-looking activity stream.

## Current-state reconstruction

Resolve live master SHA, target immutable head SHA, merge-base/ahead-behind, changed paths, current PR/issue context, current-SHA runs/jobs/steps/artifacts/reviews, and applicable governance/skill/lane SSOTs.

Prefer exact file/symbol/PR/issue/label/scope/permalink roots. Separate verified relationships from candidates.

## Evidence hierarchy

1. current-SHA diff/contracts
2. current-SHA tests/validation
3. current-SHA workflow/job/step/artifact evidence
4. substantive current-SHA review findings
5. provenance and task lineage
6. superseded historical evidence
7. size/age/comment/activity metadata only as context

Workflow success proves that workflow result; it does not prove the requested task outcome.

## State separation

PASS | FAIL | UNKNOWN | WARNING | SKIPPED | STALLED

Classify dispatch, execution, provider availability, quota/capacity, correctness, tests, integration, review, deployment, and task outcome independently.

## Adaptive WAIT

Use the adaptive-wait skill. Re-fetch after material changes; back off only on live/no-delta evidence; retry only with an evidence-backed changed hypothesis/input; keep disjoint work moving; stop on terminal state, stagnation, or missing authority/input.

## Mutation discipline

Re-read before write. Make the smallest bounded change. Run git diff --check plus the smallest relevant deterministic validation. Commit specifically. Re-fetch the resulting SHA and checks. Preserve failed/superseded evidence.

Never force-push, reset, delete evidence, or silently overwrite another active state.

## Promotion

Require current-SHA base alignment, relevant tests/invariants, finding disposition, integration/task outcome, and repository-defined dual gates.

COMMITTED, EXECUTED, VALIDATED, and PROMOTED are independent states.

## Historical continuity

Bounded history must retain page/window bounds, continuation state, timestamp, source/ref, failures, exclusions, and coverage. Partial history is never complete history.

## Receipt

Record operation, repo, base_sha, head_sha, observed_at, evidence IDs, state, outcome, provenance/confidence, decision, reason, and remaining unproven work. Receipts are projections; the longitudinal corpus is the historical source.

**Related:** adaptive-wait, adaptive-feedback-cycle, review-loop, context-relationship-graph, production-reconciliation, action-effectiveness-ledger, evidence-envelope, evidence-provenance, workflow-orchestration, evolutionary-replay.