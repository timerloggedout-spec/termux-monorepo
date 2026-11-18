# ICM Map Maintenance — Pipeline Contract

The flow is **inventory → design → verify → promote**. It maintains the System map as a documentation layer; it does not reorganize the source tree, modify application code, or turn generated/device artifacts into map content.

This is a repository-native FA-ADE workflow: agents execute the authorized scope through all four stages, using deterministic checks and repository evidence as the progression criteria. Intermediate artifacts are not human approval queues.

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

Scan stage output directories in order. The latest stage holding a non-`.gitkeep` artifact is the current state; a promotion record indicates the recorded promotion state, not merely a commit or queued workflow.

Expected progression:

`REQUESTED → INVENTORIED → PROPOSED → VERIFIED → PROMOTABLE → PROMOTED`

Use `BLOCKED` with a concrete reason when required evidence is missing, a check fails, the task outcome is unverified, or a human-only permission boundary is reached. Do not convert `queued` or `in_progress` into success. Apply adaptive WAIT and re-fetch the exact head SHA and its check/run evidence before classifying the result.

## Human-only boundary

No routine stage requires a human evaluation or sign-off. Stop only for an action explicitly reserved by root `CLAUDE.md` and `docs/proposals/AGENTIC-PERMISSIONS.md` (for example credential/provider login, destructive history operations, protected settings/permission grants, or device-side state), or for a genuine unresolved scope/policy conflict. Repository review and promotion follow the governing FA-ADE rules; this map pipeline does not add an extra approval layer.
