# AGENTS.md

<!-- #HEADER: Linguist / technical surface — not primary agent entry -->

**Not the primary entry.** Agents and operators start at **[`CLAUDE.md`](CLAUDE.md)**.

This file is the optional technical deep-dive and Linguist-visible documentation surface. It remains for tooling that still looks for `AGENTS.md`, and for humans who want the long codebase overview.

## Start here instead

1. [`CLAUDE.md`](CLAUDE.md) — governance + hard rules
2. [`docs/icm/CLAUDE.md`](docs/icm/CLAUDE.md) — task routing to one card

## What this file still holds

- Expanded project overview and statistics
- Core project tour (DeepCLI, Termux Multi-Agent, ArchWiz, …)
- Historical methodology notes and workspace layout

Do **not** treat this file as the routing catalog. Routing lives in `docs/icm/CLAUDE.md` and in pinned RinDig `content-agent-routing-promptbase_fork` (Layer 0 `CLAUDE.md` → workspace CONTEXT.md).

---

# Technical Documentation (reference)

## Project Overview

This is a **Termux-based multi-agent automation monorepo** running on Android. It orchestrates AI-powered development workflows through multiple specialized CLI tools and autonomous agents.

**Core Technologies:** Python 3 (primary), Node.js (supporting), Bash, Rust (selective). Platform: Termux on Android.

**Key Architectural Components:**
1. **ArchWiz** — Central automation cockpit
2. **DeepCLI** — DeepSeek-oriented CLI
3. **Termux Multi-Agent** — Agent provisioning and orchestration
4. **CLI Synthegration** — Conversation synthesis and branching
5. **Harmonizer** — Unified automation interface
6. **Central Mapper** — AST indexing and dependency graphs

## Dual gates (must stay green)

```bash
python3 scripts/ci/repo_gate.py
python3 scripts/ci/termux_smoke.py
```

## Navigation

Prefer `docs/icm/CLAUDE.md` route tables. Secondary indexes: `archwiz/TOOL_INDEX.md`, `archwiz/CONCEPT_INDEX.md`, `workspace/llm_map/` (generated — do not hand-edit).

For any nontrivial code, workflow, consolidation, or documentation change, perform bounded context reconnaissance with [`docs/icm/processes/context-relationship-reconnaissance.md`](docs/icm/processes/context-relationship-reconnaissance.md) and the project-local [context-relationship-graph skill](.agents/skills/context-relationship-graph/SKILL.md). Keep **verified evidence** separate from scored **candidates**.

## Hard rules (mirror of CLAUDE.md)

- Target `master` for integration.
- Cite `Implements: <ITEM-ID>`.
- No wholesale mega-PR merges; extract-only.
- No Class 3/4 secrets/session artifacts in git.
