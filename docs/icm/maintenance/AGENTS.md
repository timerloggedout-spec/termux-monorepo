# ICM Map Maintenance Pipeline

This is the agent-executed, evidence-gated maintenance pipeline for the `docs/icm/` System map. It updates documentation within the application-code and generated/device artifact ownership boundaries. It follows the repository's FA-ADE operating contract: reserve human input for explicit permission and policy boundaries.

## Where things live

| Folder | What it holds |
|---|---|
| [`01_inventory/`](01_inventory/CONTEXT.md) | Canonical source inventory, file-role classification, and explicit exclusions. |
| [`02_design/`](02_design/CONTEXT.md) | A source-backed, scope-bounded map-change proposal. |
| [`03_verify/`](03_verify/CONTEXT.md) | Automated structure, link, canonical-source, twin, scope, and repository-gate evidence. |
| [`04_promote/`](04_promote/CONTEXT.md) | Current-head reconciliation, adaptive WAIT/WATCH, and FA-ADE promotion record. |
| [`../_shared/`](../_shared/CONTEXT.md) | Stable maintenance rules, source-inventory template, and verification checklist. |

## Route by what just happened

| If… | Go to | Stop at |
|---|---|---|
| a map update is requested | `01_inventory/CONTEXT.md` | a complete, source-backed inventory or a concrete blocker |
| the inventory is complete | `02_design/CONTEXT.md` | a scoped proposal that passes deterministic acceptance |
| the proposal is ready | `03_verify/CONTEXT.md` | recorded verification evidence and exact-head gate results |
| verification is clean | `04_promote/CONTEXT.md` | re-fetched promotion state or an evidence-backed blocker |
| status is requested | scan `*/output/` | the newest non-`.gitkeep` artifact and its linked SHA/run evidence |

## Execution rule

Treat the four stages as sequential evidence boundaries. Agents execute the authorized item through inventory, design, verification, commit/PR, adaptive WAIT, and promotion. Use the repository's required `repo_gate` and `termux_smoke` checks; classify queued/in-progress as pending; re-fetch the exact head and its jobs, steps, logs, and artifacts before classifying it.

## Human-only boundary

Advance routine stages through their evidence criteria. Request human input for permission edges explicitly reserved in root `CLAUDE.md` and `docs/proposals/AGENTIC-PERMISSIONS.md` (such as credential/provider login, destructive history operations, protected settings/permission grants, or device-side state), or for a genuine unresolved policy/scope conflict. Promote under the root FA-ADE rule after both required gates are green and the task outcome is verified, subject to configured repository protections.

Keep the pipeline documentation-only; route application-code refactors through their owning proposals.
