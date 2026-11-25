# ICM Map Maintenance — Pipeline Contract

The flow is **inventory → design → verify → promote**. It maintains the System map as a documentation layer while preserving source-tree ownership, application-code boundaries, and the canonical homes of generated/device artifacts.

This is a repository-native FA-ADE workflow: agents execute the authorized scope through all four stages, using deterministic checks and repository evidence as progression criteria. Treat intermediate artifacts as evidence records and advance on their automated acceptance criteria.

| Stage | Job | Working input | Output | Automated exit criteria |
|---|---|---|---|---|
| [`01_inventory`](01_inventory/CONTEXT.md) | classify authoritative sources | a scoped map-update request | `output/source-inventory.md` | Every in-scope fact has a canonical source, role, status, and explicit exclusions; unresolved source claims remain unknown. |
| [`02_design`](02_design/CONTEXT.md) | propose one map change | completed inventory | `output/map-change-proposal.md` | Proposed paths, card type, citations, first-order impact, and exclusions are explicit and within the registered work-item scope. |
| [`03_verify`](03_verify/CONTEXT.md) | test the proposed map | proposal and changed documentation | `output/verification-record.md` | Structural, link, source, twin, scope, diff, and required repository checks pass or are recorded as blockers. |
| [`04_promote`](04_promote/CONTEXT.md) | record and execute an eligible update | passing verification record and repository policy | `output/promotion-record.md` | Current-head outcome is verified, both required gates are green, and the repository's FA-ADE promotion conditions are satisfied. |

## Factory and product

| Layer | Location | Role |
|---|---|---|
| Factory | [`../_shared/`](../_shared/CONTEXT.md) | Stable maintenance rules, source-inventory template, and validation checklist. |
| Product | `*/output/` | Per-update working artifacts and machine-readable evidence. These are intentionally ignored except for `.gitkeep`. |

## State and progression

Scan stage output directories in order. The latest stage holding a non-`.gitkeep` artifact is the current state; distinguish the promotion record from commit existence and queued workflow state.

Expected progression:

`REQUESTED → INVENTORIED → PROPOSED → VERIFIED → PROMOTABLE → PROMOTED`

Use `BLOCKED` with a concrete reason when required evidence is missing, a check fails, the task outcome is unverified, or a human-only permission boundary is reached. Classify `queued` and `in_progress` as pending. Apply adaptive WAIT and re-fetch the exact head SHA and its check/run evidence before classifying the result.

## Human-only boundary

Advance routine stages through deterministic evidence and repository validation. Request human input for actions reserved by root `CLAUDE.md` and `docs/proposals/AGENTIC-PERMISSIONS.md` (for example credential/provider login, destructive history operations, protected settings/permission grants, or device-side state), or for a genuine unresolved scope/policy conflict. Route repository review and promotion through the governing FA-ADE rules.
