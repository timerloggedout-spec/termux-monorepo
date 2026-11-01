# 04_promote — record a reviewable documentation update

One job: turn a verified ICM map change into a focused, reviewable repository update and record the dual-gate validation evidence required before merge.

## Inputs

| Kind | Path | Why |
|---|---|---|
| Working | `../03_verify/output/verification-record.md` | Provides map-specific validation evidence and blockers; created by the prior run stage. |
| Reference | [`../../objects/governance/change-control.md`](../../objects/governance/change-control.md) | Defines branch, work-item, gate, and human-only boundaries. |
| Reference | [`../../../../CLAUDE.md`](../../../../CLAUDE.md) | Defines the repository’s governance sequence and dual-gate validation rule. |
| Reference | [`../../_shared/maintenance-rules.md`](../../_shared/maintenance-rules.md) | Preserves the documentation-only scope. |

## Process

1. Confirm the verification record is complete and the diff is documentation-only.
2. Update the active proposal item and stable map files, not per-run output artifacts.
3. Commit with the relevant `Implements: <ITEM-ID>` reference and update the existing review PR.
4. Validate through the dual gates (`repo_gate` + `termux_smoke`) before treating a merge as ready.
5. Write `output/promotion-record.md` with commit, PR, dual-gate validation, and unresolved baseline gates.

## Outputs

| Artifact | Location | Format |
|---|---|---|
| Promotion record | `output/promotion-record.md` | Markdown review record |
| Reviewable update | Existing feature branch / pull request | Git commit and PR state |

## Human check

A reviewer confirms scope, validation evidence, and the `master-staging` result. This stage records readiness; it never performs an automatic merge into `master`.
