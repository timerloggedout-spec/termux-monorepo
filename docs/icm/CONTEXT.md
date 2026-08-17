# termux-monorepo ICM System Map — Context

This is a **system map**, not a replacement architecture specification or an automated pipeline. Its job is to help a later editor answer **what is this component** and **what else moves if I change it** without loading the whole repository.

## Inputs

| Kind | Path | Why it is loaded |
|---|---|---|
| Static catalog aliases | [`CLAUDE.md`](CLAUDE.md) and [`AGENTS.md`](AGENTS.md) | Byte-identical stable entry points that route an edit request to one shelf. |
| Provider-routing resource | [`routing.md`](routing.md) | Separately owned nested evidence and polling-governance route; not a static alias. |
| Governance | [`../../AGENTS.md`](../../AGENTS.md) | Defines branch, proposal, and validation constraints. |
| Navigation | [`../../README.md`](../../README.md) | Owns the root navigation ladder and subsystem inventory. |
| Operations | [`../../archwiz/TOOL_INDEX.md`](../../archwiz/TOOL_INDEX.md) | Owns concise ArchWiz tool roles. |
| Stale platform context | [`objects/platform/termux-agentic-hub.md`](objects/platform/termux-agentic-hub.md) | Preserves archived Android execution-plane context; requires re-verification before any device work. |
| Maintenance factory | [`_shared/CONTEXT.md`](_shared/CONTEXT.md) | Holds stable rules and templates for documentation-only ICM map updates. |

## Reading protocol

1. Start at `CLAUDE.md` and select **one** matching card or process.
2. If the request changes the map itself, enter [`maintenance/CLAUDE.md`](maintenance/CLAUDE.md) instead of editing a card directly.
3. Read the selected card and the source paths it cites; source wins over the card if they disagree.
4. Treat `live` cards as current editing surfaces, `leftover` cards as non-primary paths, and `ghost` cards as named-but-not-wired material.
5. Use `effects/CONTEXT.md` for first-order impact only. Open further cards only when a cited source creates a concrete dependency.
6. For provider-routing work, enter [`routing.md`](routing.md) after selecting it from the static catalog; do not treat it as a substitute for current runtime configuration or workflows.
7. Run the governing validation before proposing a merge. The map records routing; it does not waive repository policy.

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
