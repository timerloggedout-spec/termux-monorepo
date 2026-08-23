# 03_verify — validate one proposed map change

One job: verify the approved documentation change against ICM structure, canonical sources, and repository scope before it is promoted for review.

## Inputs

| Kind | Path | Why |
|---|---|---|
| Working | `../02_design/output/map-change-proposal.md` | Names the approved change and expected source set; created by the prior run stage. |
| Working | Changed files named by the approved proposal | The documentation under verification. |
| Reference | [`../../_shared/verification-checklist.md`](../../_shared/verification-checklist.md) | Defines repeatable structural, source, and scope checks. |
| Reference | [`../../CONTEXT.md`](../../CONTEXT.md) | Supplies the cold-walk and universe rules. |

## Process

1. Confirm the human decision recorded for the design proposal.
2. Resolve every relative map link and verify every `verified` card’s canonical source citation.
3. Check catalog twins, context contracts, factory/product separation, and first-order effects.
4. Inspect the diff to confirm it contains documentation-only changes and no application-code refactor.
5. Record pass/fail evidence and any baseline repository-gate failures in `output/verification-record.md`.

## Outputs

| Artifact | Location | Format |
|---|---|---|
| Verification record | `output/verification-record.md` | Markdown checklist and command evidence |

## Human check

Read the verification record and confirm that the map walks cold, sources remain canonical, and any failure is either repaired or explicitly accepted as a separate baseline blocker.
