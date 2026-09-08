# Reconciliation Control Plane

Status: active design contract

## Why

The repository intentionally uses branches, tags, and immutable commits as experimental surfaces. Reconciliation must therefore be dynamic: a workflow must accept refs as data, resolve them to SHAs, compare them, and preserve each observed state. A PR-specific branch name is never a control-plane invariant.

## Plan

1. **RECON** — resolve candidate/base refs; capture SHA, merge-base, ahead/behind, timestamps, changed paths, reviews, checks, and workflow evidence.
2. **CLASSIFY** — aligned, candidate-ahead, behind, diverged, or ambiguous.
3. **PRESERVE** — snapshot evidence before any rotation or cleanup.
4. **IMPLEMENT** — restore authoritative source/docs/tests only when the comparison proves they were removed; classify generated evidence separately.
5. **EXPERIMENT** — run identical validation suites against immutable candidate/baseline SHAs.
6. **COMMIT** — make the smallest forward correction; never rewrite master history.
7. **WAIT** — allow Actions/review providers to finish.
8. **VALIDATE** — re-fetch by current SHA and evaluate terminal check/review state.
9. **REPEAT** — continue until the stop criteria are satisfied.

## Stop-on-conflict rule

A diverged graph is not a failure to be hidden. It is an explicit state requiring a reviewed reconciliation strategy. The engine must not force-push, reset, delete evidence, or silently choose a side.

## Rollback versus recovery

A large deletion may be a rollback, intentional refactor, generated-artifact rotation, or loss of evidence. The engine compares exact paths and commit ancestry before classifying it. Recovery restores only evidence-backed authoritative material. Generated telemetry is append-only evidence and must retain provenance.

## MVT / DOE

`experiment_id`, candidate SHA, baseline SHA, suite, manager/policy version, task family, cohort, result, and provenance confidence form the minimum experiment record. Branch names are labels, not identities.

## Modular Actions

Prefer reusable composite actions and thin orchestrator workflows over a growing set of bespoke PR-specific workflows. GitHub workflow count/size constraints should be treated as an architectural signal: consolidate shared discovery, evidence capture, retry policy, classification, and validation primitives while keeping privileged mutation lanes isolated.

## External coordination

- GitHub: source of truth for refs, PRs, reviews, checks, Actions evidence, and commits.
- Linear: execution/project coordination; link work by issue key and Git SHA.
- Notion: human-facing cockpit/runbook and research synthesis; do not make it the authoritative commit/check ledger.
- Hex: comparative analysis of experiment/evidence datasets; publish conclusions with experiment IDs and source SHAs.
- Vercel: deployment/preview evidence; distinguish deployment health from repository correctness and rate-limit/provider failures.

## Skill hierarchy

Operational skills live beside the control-plane contracts. A skill may define procedure, but the repository evidence and current SHA remain authoritative. `SKILL.md` files must be concise, executable, and point to canonical scripts/workflows rather than duplicating implementation.
