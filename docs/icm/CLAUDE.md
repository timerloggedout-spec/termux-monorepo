# termux-monorepo ICM System Map

This is the agent-navigable system map for `termux-monorepo`. It routes an editor to the smallest authoritative source set needed to understand a component or plan a change; source code, governing documents, and generated indexes remain the sources of truth.

Built with the integrated [ICM Architect](../../refTemplates/smods/icm-architect_fork/README.md) method: hierarchy scopes context, cards record change impact, and the filesystem makes the current documentation surface inspectable.

## Where things live

| Shelf | What it holds |
|---|---|
| [`objects/platform/`](objects/platform/CONTEXT.md) | The Android/Termux execution plane and its boundary. |
| [`objects/operations/`](objects/operations/CONTEXT.md) | ArchWiz and the bounded operational tool surface. |
| [`objects/knowledge/`](objects/knowledge/CONTEXT.md) | Navigation, indices, and generated-map boundaries. |
| [`objects/governance/`](objects/governance/CONTEXT.md) | Branch, proposal, validation, and approval constraints. |
| [`processes/`](processes/CONTEXT.md) | Real editor workflows with explicit inputs and outputs. |
| [`effects/`](effects/CONTEXT.md) | A compact “if you change X, read Y” index. |
| [`maintenance/`](maintenance/CLAUDE.md) | A human-gated, documentation-only pipeline for future map updates. |

## Route by task

| If you need to… | Read | Then stop at |
|---|---|---|
| orient before a change | [`CONTEXT.md`](CONTEXT.md) | the one relevant object or process card |
| change the Android execution plane | [`objects/platform/termux-agentic-hub.md`](objects/platform/termux-agentic-hub.md) | the cited architecture source |
| change ArchWiz or a verification tool | [`objects/operations/archwiz.md`](objects/operations/archwiz.md) | the cited tool catalog or source path |
| alter navigation or an index | [`objects/knowledge/navigation-and-indexes.md`](objects/knowledge/navigation-and-indexes.md) | the owning navigation/index file |
| modify tracked code or documentation | [`processes/change-and-validate.md`](processes/change-and-validate.md) | the required human gate |
| assess first-order change impact | [`effects/CONTEXT.md`](effects/CONTEXT.md) | the linked object/process card |
| maintain or extend the ICM map | [`maintenance/CLAUDE.md`](maintenance/CLAUDE.md) | the `02_design` human gate |

## One rule

Read this catalog, one relevant card, and its cited sources. Do **not** crawl the monorepo or treat generated maps, recovery notes, or untracked device state as substitute sources of truth.
