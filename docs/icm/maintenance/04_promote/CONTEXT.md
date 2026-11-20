<!-- LinguistProjection: generated; source=docs/icm/maintenance/04_promote/CONTEXT.hum.md; mode=machine-grimoire-seed-v1; structural-exceptions=fenced-code,markdown-link-destinations -->

# 04_promote — record a reviewable §0a§ update

One job: turn a verified ICM map change into a focused, reviewable §19§ update and record the master-staging §1d§ evidence required before any later master merge.

## Inputs

| Kind | §14§ | Why |
|---|---|---|
| Working | `../03_verify/output/verification-record.md` | Provides map-specific §1d§ evidence and blockers; created by the prior run stage. |
| Reference | [`../../objects/governance/change-control.md`](../../objects/governance/change-control.md) | Defines §04§, work-item, gate, and human-only boundaries. |
| Reference | [`../../../../§02§.md`](../../../../AGENTS.md) | Defines the §19§’s governance sequence and `master-staging` §1d§ rule. |
| Reference | [`../../_shared/maintenance-rules.md`](../../_shared/maintenance-rules.md) | Preserves the documentation-only scope. |

## §17§

1. Confirm the verification record is complete and the diff is documentation-only.
2. Update the active proposal item and stable map §a1§, not per-run output artifacts.
3. Commit with the relevant `Implements: <ITEM-ID>` reference and update the existing §1a§ PR.
4. Validate through the `master-staging` §14§ before treating a later `master` merge as ready.
5. Write `output/promotion-record.md` with commit, PR, master-staging §1d§, and unresolved baseline gates.

## Outputs

| Artifact | Location | Format |
|---|---|---|
| Promotion record | `output/promotion-record.md` | Markdown §1a§ record |
| Reviewable update | Existing feature §04§ / pull request | Git commit and PR state |

## §0e§ check

A reviewer confirms scope, §1d§ evidence, and the `master-staging` result. This stage records readiness; it never performs an automatic merge into `master`.
