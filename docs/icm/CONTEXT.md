# termux-monorepo ICM System Map — Context

This is a **system map**, not a replacement architecture specification or an automated pipeline. Its job is to help a later editor answer **what is this component** and **what else moves if I change it** without loading the whole repository.

## Inputs

| Kind | Path | Why it is loaded |
|---|---|---|
| Catalog | [`CLAUDE.md`](CLAUDE.md) | Routes the edit request to one shelf. |
| Governance | [`../../AGENTS.md`](../../AGENTS.md) | Defines branch, proposal, and validation constraints. |
| Navigation | [`../../README.md`](../../README.md) | Owns the root navigation ladder and subsystem inventory. |
| Operations | [`../../archwiz/TOOL_INDEX.md`](../../archwiz/TOOL_INDEX.md) | Owns concise ArchWiz tool roles. |
| Platform | [`../architecture/termux-agentic-hub.md`](../architecture/termux-agentic-hub.md) | Owns the Android execution-plane architecture. |

## Reading protocol

1. Start at `CLAUDE.md` and select **one** matching card or process.
2. Read that card and the source paths it cites; source wins over the card if they disagree.
3. Treat `live` cards as current editing surfaces, `leftover` cards as non-primary paths, and `ghost` cards as named-but-not-wired material.
4. Use `effects/CONTEXT.md` for first-order impact only. Open further cards only when a cited source creates a concrete dependency.
5. Run the governing validation before proposing a merge. The map records routing; it does not waive repository policy.

## Universes and name collisions

| Term | Meaning in this map |
|---|---|
| `live` | Tracked code or documentation currently named by the navigation and governance sources. |
| `leftover` | Recovery, historical, backup, or legacy material that remains present but is not the main implementation path. |
| `ghost` | Reserved concepts, future work, or named integrations that are not wired as the current path. |
| Termux runtime | The Android execution plane, not this Linux-based documentation worktree. |
| `hub_mcp` | The policy and validation boundary for structured jobs, not a generic interactive remote shell. |
| system map | This linked edit map; it is distinct from generated `workspace/llm_map` outputs. |

## Human check

A reviewer should be able to read `CLAUDE.md` plus one card and answer where the source of truth lives, what is in scope, and the first-order impact before any code or configuration is changed.
