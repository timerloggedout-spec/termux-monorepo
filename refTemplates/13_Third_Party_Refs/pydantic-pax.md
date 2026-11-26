# Pydantic Pax — refTemplates entry (pattern from Pydantic AI Harness)

- **What:** Pax — Pydantic's official terminal coding agent (TUI), built on the Pydantic AI Harness SDK. Everything in it is a plugin — the coding agent itself included — and it can import Claude Code and Codex sessions and continue them on any model.
- **Source:** Pydantic launch article, 2026-11-25 — https://pydantic.dev/articles/pax-harness-beta · Docs — https://pydantic.dev/docs/ai/pax/ · Implementation — https://github.com/pydantic/pydantic-ai (`src/pydantic_ai_pax`, `src/pydantic_ai_harness`) · Package — https://pypi.org/project/pydantic-ai-pax/
- **Status (QUE #5591 standing mandate):** INTAKE ONLY — inspiration + inspection, never a dependency, no vendoring. Adoption, if any, is a separate DoE-scored leg (#5590-class), not this entry.

## The pattern (what we copy)

- **Everything is a plugin; the agent is a plugin.** A Pax plugin is a Pydantic AI *capability* one layer up: agent-side tools + hooks, plus terminal pieces (`/commands`, status-bar items, logins). The stock coding agent ships as the toggleable `coder` plugin (`pydantic_ai_pax.builtin_plugins.coder`); `/plugins disable coder` leaves a clean chat client with no file or shell tools. Built-ins on by default: `coder`, `ask_user`, `repo_context`, `compaction`, `refinement`, `persistence`, `mcp`, `notifications`, `observability` (Logfire tracing); more (`github`, `linear`, `notion`, `slack`, …) toggle on.
- **One composition primitive: the capability.** The Harness is a library of 100+ capabilities — bundles of tools, instructions, and hooks snapped onto any agent. `Coder()` itself is a *combined* capability, decomposable into its blocks (`FileSystem`, `Shell`, `RepoContext`, `SubAgents`, `ClearToolResults`, `ToolOutputLimits`, `RepairToolArguments`) — use it whole or use the parts; the two are equivalent.
- **Four-layer stack, each layer independently usable:** `pydantic-ai` (agent loop, every provider's models, structured output) → `pydantic-ai-harness` (workspaces, file/shell tools, memory, sub-agents, context management, durable execution, computer use, model fallback incl. refusal-catching, code mode) → `Coder` (the coding harness as one capability) → Pax (the terminal in front). Each package installs the one below it.
- **Bring your own agent.** `pax --agent my_agents:reviewer` replaces the stock agent with any Pydantic AI `Agent` from your codebase — no Pax plugins load, the agent runs as-is with its own model/tools/instructions, and the exact same `Agent` object ships in your service. Programmatic forms: `open_stock_agent(...)`, `chat(agent, deps=...)`, `pax -p "…"` for one-shot runs.
- **Workspace abstraction.** File/shell tools talk to a Workspace, never the metal: `LocalWorkspace('.')` swaps for `E2BSandbox` (or boxd, daytona, opensandbox, modal, render, sprites, kubernetes; local smol/BoxLite micro-VMs) with no tool-code change. In Pax, `/sandbox <provider>` swaps where a session runs before the first prompt; branch + uncommitted diff sync in, and on proxy-enabled providers the egress proxy injects the GitHub token so it never enters the sandbox.
- **Conversation import = session portability.** `/resume` lists Claude Code and Codex sessions next to Pax's own; `pax --resume-claude` / `pax --resume-codex` (also `/resume claude|codex`) imports one and continues it on any model. Repo setup carries over: `repo_context` reads `AGENTS.md`/`CLAUDE.md`, and the `coder` plugin loads Agent Skills from `.agents/skills` and `.claude/skills`.
- **Model + account agnosticism.** Models switch mid-conversation (`/model`); multiple accounts per provider are profiles (`PROVIDER@PROFILE`, e.g. `openai-codex@work`) and a run moves to the next account on a rate/usage limit; user-built fallback chains (`chain:NAME`) try models in order. Sign-in via ChatGPT or GitHub Copilot subscription, or API keys (named, encrypted in a keychain-backed store; shell commands the agent runs never see provider keys).
- **Code mode + speculative execution.** Default on: instead of one tool call per turn, the model writes a short Python snippet (run in Monty, Pydantic's sandboxed interpreter) that calls many tools; statements execute as they stream. Speculative execution (Ctrl+X, Ctrl+S) starts safe file reads/searches while the model is still streaming, with hit/miss/wasted accounting in the status row.
- **Persistence as substrate.** Every conversation is saved (`sessions.db`; settings/trust/plugin choices in `config.db`, under `~/.config/pydantic-clai2/`): resume, rewind-to-earlier-prompt, `/fork` into background (optionally on another model). At the SDK layer, `StepPersistence` snapshots every settled step; durable execution (Temporal/DBOS/Prefect) exists in the framework — explicitly not in Pax yet.
- **Self-extending.** Plugins install from Git (`/plugins add <git-url>`), by capability import path with JSON config (`/plugins add exa pydantic_ai_harness.exa:ExaSearch '{…}'`), or as drop-in files (`~/.config/pydantic-clai2/plugins/`). Pax carries its own plugin guide and can write new plugins for itself on request.

## Maturity signals (at intake, 2026-11-26)

- Beta: launch article is a beta call-for-testing; the Harness targets 1.0 "in about a month" under Pydantic AI's version policy. Pax version in the launch capture: `pydantic-ai-pax` 0.75.0.
- Repo `pydantic/pydantic-ai`: MIT license, ~21.4k stars, 6,104 commits, 364 releases — a high-activity monorepo; Pax + Harness live in-tree (`src/pydantic_ai_pax`, `src/pydantic_ai_harness`), renamed from the earlier `pydantic-clai2` package (old names still work, settings/sessions/plugins carry over).
- Install surface: Python ≥3.11, `uv tool install --compile-bytecode pydantic-ai-pax` or `uvx pydantic-ai-pax`; in-product updates (`/update`, stable + main channels).
- Vendor benchmark claims (single November runs, relaxed rescore, NOT fleet numbers): Harness-Bench SWE81 average 58.5 across 8 models — highest of the four harnesses that ran all eight, narrowly; $9.21/run vs Codex $21.05 on GPT-6.2 Sol; $24.61 vs Claude Code $25.10 on Claude Opus 5.5.
- Safety posture, as documented: locally Pax runs commands and edits files as the user, with no sandbox and no approval step — "run it in a project you trust"; per-folder trust prompt gates how repo files are treated.

## Fleet mapping (candidate fits — unscored, intake only)

- **Capability/plugin composition** ↔ the fleet's surface composition: one bundle primitive (tools + instructions + hooks) that assembles agents, with the agent itself just the largest bundle — the same shape as fleet actors assembled from shared parts rather than hand-built per surface.
- **Agent-as-plugin toggle** ↔ surface swap discipline: disabling `coder` to get a clean chat client mirrors running a wrapped session as pure participant vs full actor.
- **Session import across harnesses** ↔ the fleet's multi-surface session problem (ChatGPT/Codex/Claude/Jules sessions as one portable record): Pax's answer is read-the-other-tool's-session-store + continue on any model — a concrete implementation to inspect for the Provenance/session-store legs.
- **Workspace swap + token-injecting egress proxy** ↔ mesh surfaces: run the same agent on any surface, credentials injected at the boundary and never resident in the sandbox (the fleet's wrapper-boundary rule, implemented by a third party).
- **Account profiles + limit failover** ↔ quota-aware routing: ordered multi-account failover on rate/usage limits is the consumer-grade form of the fleet's pre-flight headroom discipline.

## Bounds

- Pattern + inspection only: no dependency, no vendoring, no code lifted; any adoption goes through DoE scoring as its own leg.
- Vendor internals (Monty, Logfire, the Harness capability catalog) are referents, not fleet commitments.
- Benchmark figures above are the vendor's own single-run claims, recorded as claims.
