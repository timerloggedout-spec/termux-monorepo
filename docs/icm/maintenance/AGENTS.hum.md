# ICM Map Maintenance Pipeline

This is the documentation-only maintenance pipeline for the `docs/icm/` System map. It turns a proposed map update into a reviewed, verified, and promotable documentation change without refactoring application code or treating generated/device artifacts as pipeline output.

## Where things live

| Folder | What it holds |
|---|---|
| [`01_inventory/`](01_inventory/CONTEXT.md) | The source inventory and file-role classification for the requested map update. |
| [`02_design/`](02_design/CONTEXT.md) | The proposed card/route change and the human approval checkpoint. |
| [`03_verify/`](03_verify/CONTEXT.md) | Link, canonical-source, one-way-reference, and walk-test evidence. |
| [`04_promote/`](04_promote/CONTEXT.md) | The gated commit and PR update record. |
| [`../_shared/`](../_shared/CONTEXT.md) | Stable maintenance rules and source inventory templates. |

## Route by what just happened

| If… | Go to | Stop at |
|---|---|---|
| a map update is requested | `01_inventory/CONTEXT.md` | a reviewed inventory artifact |
| the inventory is complete | `02_design/CONTEXT.md` | human approval or explicit revision |
| the design is approved | `03_verify/CONTEXT.md` | recorded verification evidence |
| verification is clean | `04_promote/CONTEXT.md` | a reviewable, documentation-only commit |
| status is requested | scan `*/output/` | the newest non-`.gitkeep` artifact |

## One rule

Nothing advances beyond `02_design` until a human has read the proposed documentation change. The maintenance pipeline may add or revise map documentation; it must not refactor application code.
