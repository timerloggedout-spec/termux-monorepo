# ICM Map Maintenance — Pipeline Contract

The flow is **inventory → design → verify → promote**. It maintains the System map as a documentation layer; it does not reorganize the source tree, modify application code, or turn generated/device artifacts into map content.

| Stage | Job | Working input | Output | Human check |
|---|---|---|---|---|
| [`01_inventory`](01_inventory/CONTEXT.md) | classify authoritative sources | a scoped map-update request | `output/source-inventory.md` | Sources, roles, and universes are accurate. |
| [`02_design`](02_design/CONTEXT.md) | propose one map change | approved inventory | `output/map-change-proposal.md` | A human approves, rejects, or edits the proposal. |
| [`03_verify`](03_verify/CONTEXT.md) | test the proposed map | approved proposal and changed documentation | `output/verification-record.md` | Links, citations, and the cold walk are sound. |
| [`04_promote`](04_promote/CONTEXT.md) | record the reviewable update | verification record and repository policy | `output/promotion-record.md` | Commit/PR scope and gate evidence are ready for review. |

## Factory and product

| Layer | Location | Role |
|---|---|---|
| Factory | [`../_shared/`](../_shared/CONTEXT.md) | Stable maintenance rules, source-inventory template, and validation checklist. |
| Product | `*/output/` | Per-update working artifacts and human decisions. These are intentionally ignored except for `.gitkeep`. |

## Status

Scan stage output directories in order. The latest stage holding a non-`.gitkeep` artifact is the current state; a promotion record indicates a reviewable update, not an automatic merge.

## Human check

A person must approve the `02_design` proposal before the verification stage or repository change proceeds. Human review remains mandatory for scope changes and final promotion.
