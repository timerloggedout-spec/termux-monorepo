<!-- LinguistProjection: generated; source=docs/icm/maintenance/03_verify/CONTEXT.hum.md; mode=machine-grimoire-seed-v1; structural-exceptions=fenced-code,markdown-link-destinations -->

# 03_verify — validate one proposed map change

One job: §1f§ the approved §0a§ change against ICM structure, canonical sources, and §19§ scope before it is promoted for §1a§.

## Inputs

| Kind | §14§ | Why |
|---|---|---|
| Working | `../02_design/output/map-change-proposal.md` | §a2§ the approved change and expected source set; created by the prior run stage. |
| Working | Changed §a1§ named by the approved proposal | The §0a§ under verification. |
| Reference | [`../../_shared/verification-checklist.md`](../../_shared/verification-checklist.md) | Defines repeatable structural, source, and scope checks. |
| Reference | [`../../§08§.md`](../../CONTEXT.md) | Supplies the cold-walk and universe rules. |

## §17§

1. Confirm the §0e§ decision recorded for the design proposal.
2. Resolve every relative map link and §1f§ every `verified` card’s canonical source citation.
3. Check catalog twins, §08§ contracts, factory/product separation, and first-order effects.
4. Inspect the diff to confirm it contains documentation-only changes and no application-code refactor.
5. Record pass/fail evidence and any baseline repository-gate failures in `output/verification-record.md`.

## Outputs

| Artifact | Location | Format |
|---|---|---|
| Verification record | `output/verification-record.md` | Markdown checklist and §06§ evidence |

## §0e§ check

Read the verification record and confirm that the map walks cold, sources remain canonical, and any failure is either repaired or explicitly accepted as a separate baseline blocker.
