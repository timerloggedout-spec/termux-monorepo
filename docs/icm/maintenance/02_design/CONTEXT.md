# 02_design — propose one map change

One job: convert a completed source inventory into a minimal, reviewable documentation proposal within the documentation-only boundary and registered scope.

## Inputs

| Kind | Path | Why |
|---|---|---|
| Working | `../01_inventory/output/source-inventory.md` | Defines the bounded source set and candidate card; created by the prior run stage. |
| Reference | [`../../_meta/schema.md`](../../_meta/schema.md) | Defines card types, universes, and verification status. |
| Reference | [`../../_templates/object.md`](../../_templates/object.md) and [`../../_templates/process.md`](../../_templates/process.md) | Provide the blank card shapes. |
| Reference | [`../../_shared/maintenance-rules.md`](../../_shared/maintenance-rules.md) | Keeps the proposal canonical, one-way, documentation-only, and aligned with FA-ADE. |
| Governance | [`../../../../docs/proposals/active/icm-architect-integration/ITEMS.md`](../../../../docs/proposals/active/icm-architect-integration/ITEMS.md) | Defines the authorized ICM work-item scope. |

## Process

1. Select one addition or revision supported by the inventory.
2. Write `output/map-change-proposal.md` with the proposed location, card type, source citations, first-order Hits/Does not hit, and links to update.
3. State every intended documentation file change and every explicitly excluded code/source file.
4. Check that the proposal fits the registered item, canonical ownership, one-way-reference policy, and ICM schema.
5. Advance to verification when the proposal passes these checks; reserve human review for explicit permission and policy boundaries.

## Outputs

| Artifact | Location | Format |
|---|---|---|
| Map-change proposal | `output/map-change-proposal.md` | Markdown with source citations, change list, scope mapping, and acceptance evidence |

## Automated acceptance

- Every proposed edit is supported by the inventory and canonical sources.
- The change list is complete and remains within the authorized item.
- First-order impact and exclusions are explicit.
- Keep application-code, generated-index, credential, and device-state mutations outside the proposed change.
- The proposal is deterministic enough for a second agent/checker or repository validation to verify.

If scope is materially ambiguous, sources conflict, or the change crosses a human-only permission boundary, record the exact blocker. Assign ordinary design choices and proposal review to the agent workflow; escalate human-only boundaries.
