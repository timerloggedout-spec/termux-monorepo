# lane-consolidation-ssot — Master Coordination & Production Improvements Map

**Date:** 2026-08-10
**Status:** ACTIVE
**Orchestration Profile:** Grok / Jules Automated Operations
**Authority Level:** Production Consolidated SSOT

---

## 1. Executive Summary & Production Objectives

To maximize return on investment (ROI) and maintain impeccable repository hygiene, this Single Source of Truth (SSOT) consolidates active and closed development lanes, aligns timing quotas and cooldowns, and maps open/closed pull requests and issues to clear, insulated scopes.

### Core Targets
- **Zero overlapping work-areas:** Delineate exact folder ownership to avoid multi-agent merge conflicts.
- **Quota resilience:** Maximize utilization of free-tier AI pathways (Omni, OpenRouter, Gemini) without hitting hard rate limits (429).
- **Consolidated dispatch pipeline:** Ensure all local command-line interfaces and background orchestrators map through config-rooted endpoints, enforcing strict privilege controls (Sentinel 0o600/0o700 limits).

---

## 2. Timing Quotas, CoolDowns & Soft-Limits Optimization Matrix

To optimize API usage and ensure stable CI/CD runs, the repository implements a multi-tiered timing, caching, and debounce schema across all automated GitHub Actions workflows.

### 2.1 Model Router Soft-Limits (Elevated 2026-08-10)
Model routing is controlled via `scripts/model_router.py` using dynamic ELO-based (3L0) ranking, 1-hour temporal caching, and soft budgets defined in `.github/connectors/llm-peers.yaml`.

| Provider / Model | Triage Limit | Review Limit | Invoke Limit | Role Suitability |
|------------------|--------------|--------------|--------------|-------------------|
| **omni/auto/best-free** | **400** | **250** | **400** | Primary free peer (all roles) |
| **openrouter/google/gemma-4-31b-it:free** | **80** | **80** | **80** | Triage, Review, Invoke |
| **openrouter/google/gemma-4-26b-a4b-it:free** | **80** | **80** | **80** | Triage, Review, Invoke |
| **openrouter/meta-llama/llama-3.3-70b-instruct:free** | **80** | **80** | **80** | Triage, Review, Invoke |
| **openrouter/google/gemma-3-12b-it:free** | **80** | **80** | **80** | Triage, Review, Invoke |
| **openrouter/cohere/north-mini-code:free** | **60** | **60** | **60** | Review, Invoke |
| **openrouter/qwen/qwen3-coder:free** | **60** | **60** | **60** | Review, Invoke |
| **openrouter/deepseek/deepseek-r1:free** | **40** | **40** | **40** | Review (specialized) |
| **gemini/gemini-3.1-flash-lite** | **450** | **450** | **450** | Residual backup |
| **gemini/gemini-3.5-flash-lite** | **450** | **450** | **450** | Residual backup |
| **gemini/gemini-2.5-flash-lite** | **20** | **20** | **20** | Secondary residual |
| **gemini/gemini-3.5-flash** | **20** | **20** | **20** | Secondary residual |
| **gemini/gemini-2.5-flash** | **20** | **20** | **20** | Secondary residual |
| **gemini/gemini-3-flash** | **20** | **20** | **20** | Secondary residual |

*Note: Newly listed free models must appear in the live OpenRouter models poll before they can be dynamically selected. Conservative fallback `LEGACY_MODELS` is used if polling fails.*

### 2.2 GitHub Actions Debounces & Sweep Throttles

```
[External Bot Feedback]
       │
       ▼
[peer-review-orchestrator.yml] ──► Holds run for review completion (up to 480s)
       │
       ├─► 45-Minute Throttle ───► Debounces Auto-CodeRabbit Autofix comments
       │
       └─► 90-Second Settle ─────► Pauses to allow autofix commit push before second-pass
       │
       ▼
[agent-review-auto-jules.yml] ───► 20-Minute Debounce prevents redundant @jules summon pings
```

#### A. Peer Review Orchestrator (`peer-review-orchestrator.yml`)
- **Max Wait Time:** `480 seconds` (8 minutes) waiting for external peer bots (CodeRabbit, Devin, Aikido, Sentry, Copilot) to complete checks.
- **Autofix Request Throttle:** `45 minutes` per PR. If an autofix marker is present, comments requesting `@coderabbitai autofix` are bypassed.
- **Settle Cooldown:** `90 seconds` sleep delay after posting an autofix request to allow background file writing to complete before subsequent jobs trigger.

#### B. Agent Review Auto-Jules (`agent-review-auto-jules.yml`)
- **Summon Debounce Window:** `20 minutes` per PR. Ensures Jules is not double-summoned by rapid succession review comments.
- **Trigger Profiles:** Runs on any non-approved `pull_request_review` or review/issue comment created by a Bot (except our own markers).

#### C. Continuous Agent Ops Sweep (`agent-continuous-ops.yml`)
- **Schedule Interval:** Every `2 hours` (scheduled cron: `17 */2 * * *`).
- **Sweep Debounce Window:** `90 minutes` per PR. Ensures a PR is not spammed by continuous sweep comments if it was recently processed.
- **Unattended Activity Age Limit:** `3 hours` stale duration (agent must have been inactive for at least 3 hours with open threads/conflicts before sweep acts).
- **Sweep Capacity Cap:** Max `8` PRs processed per scheduled run (hard limit `20`) to respect API rate limits and quotas.

---

## 3. Pull Request & Issue Audit (Unified Map)

Based on live GitHub tracking and active repository branches, open and closed items are consolidated into clear development lanes.

### 3.1 Open Pull Requests (Live Audit)
1. **PR #149** (`ops(pipes): review-signal alignment docs + disposition matrix`): Focuses on aligning review signals and continuous-ops logic.
2. **PR #148** (`ops(jules): context_key persistence + continue-only auto-jules`): Adds programmatic context and dual-quota gating limits (3 concurrent, 15/24 hours rolling) using cached context stores.
3. **PR #147** (`Programmatic session management via Actions Workflows`): Wire automatic context tracking for Jules.
4. **PR #143** (`Integrate MCP Agent Mail Coordination Layer in GitHub Actions`): Rust-based agent mailbox coordination in workflows.
5. **PR #142** (`⚡ Bolt: Optimize telemetry parsing with state-tracking and seek/tell`): Optimizes real-time dashboard reading performance.
6. **PR #141** (`🛡️ Sentinel: Fix local privilege restrictions and prevent symlink hijacking`): Security hardening of permission walkers.
7. **PR #140** (`🎨 Palette: Stateful & Reactive PWA UX with Manual Vault Refresh`): Reactive web UI state for Commingle Swarm.
8. **PR #137** (`feat(ci): integrate DeepSeek v4-Pro CI with peer routing`): Plumbs reverse-engineered web-wrapper and peer routes.
9. **PR #135** (`📝 CodeRabbit Chat: Align OpenRouter Routing with Supported Models`): Adjusts OpenRouter free model catalogs.
10. **PR #133** (`Diagnose Issue #129 and Verify Codebase Integrity`): Checks telemetry logs and system map.
11. **PR #131** (`feat(multi-agent): implement MoneyBall agent roster`): Team roster bidding/betting arena algorithms.
12. **PR #126** (`📖 Linguist: optimize agentic communication compiler`): CedrLang O(N) translation and markdown compression.

### 3.2 Active Issue Threads & Alignment
- **Issue #59** (`🚨 CRITICAL: GitHub Actions Workflow Failures`): Resolves Gemini free-tier daily exhaustion via `continue-on-error: true`.
- **Issue #122** (`Model Availability Polling`): Enforces temporal polling caches in `/tmp/model-router`.
- **Issue #86** (`Rate Limits and Model Rotations Optimizations`): Elevated model router budgets (Operator 2026-08-10).
- **Issue #146** (`ops(pipes): Align review disposition`): Maps directly to PR #149 signal alignment.
- **Issue #145** (`ops(jules): Programmatic session management`): Maps directly to PR #148 context keys.
- **Issue #130** (`Model Performance diagnostics`): Addressed by Bolt's telemetry parsing optimizations (state-tracking + seek/tell).
- **Issue #129** (`Development Teams & Emerging Tech Research`): Addressed by MoneyBall betting arena (PR #131).
- **Issue #124** (`Workflows @ call; received`): Tracks pending notifications during long-running GHA orchestrations.
- **Issue #117** (`Agent2Agent Comms Proposal`): Solved by MCP Agent Mail composite GHA mailbox actions.
- **Issue #110** (`Nested Searches`): Powered by Virtual FTS5 tables (`messages_fts` in `local_repo.db`).
- **Issue #109** (`DeepSeek v4-Pro integration`): Tracked in PR #137 CI pipeline.

---

## 4. Development Lanes & Scope Clarification

To keep work highly organized, all development is segregated into five independent Lanes. No agent may touch a file outside their active lane's domain without explicit coordination.

```
                  ┌──────────────────────────────┐
                  │      Dual-Gate Spine         │
                  │  (repo-gate + termux-smoke)  │
                  └──────────────┬───────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
┌──────────────────┐   ┌──────────────────┐    ┌──────────────────┐
│ Performance Lane │   │  Security Lane   │    │  Reactive PWA    │
│  (Bolt / Lithe)  │   │    (Sentinel)    │    │ (Palette / Swarm)│
└──────────────────┘   └──────────────────┘    └──────────────────┘
```

### Lane 1: Performance Optimization & Telemetry (Bolt / Linguist)
- **Primary Scope:** `termux-multi-agent/dashboard.py`, `agent_telemetry_stream.json`, `cedrlang.py`.
- **Core Guardrails:**
  - Real-time display MUST utilize `rich.live.Live` and `rich.console.Group` to prevent terminal flicker.
  - Telemetry logs MUST use state-tracking and seek/tell incremental I/O (no O(N) full-read repeats).
  - Markdown compression (CedrLang) compiler MUST enforce O(N) regex matching and a 6-line caveman stopword list.
- **Active Agent:** Bolt / Linguist.

### Lane 2: Security & Local Privilege (Sentinel)
- **Primary Scope:** `deepcli/deepcli/core.py`, `tests/test_sentinel_privileges.py`, configuration directories, database connections.
- **Core Guardrails:**
  - Configuration directory MUST be `0o700` and config files/cached session files MUST be `0o600`.
  - Recursive directory-walking permissions adjusters MUST explicitly skip symlinks (`path.is_symlink()`) to prevent symlink traversal hijacking vulnerabilities.
  - Security-sensitive environments checks (e.g. `JULES_API_KEY`) must remain strictly boolean-only (no storage or console exposure).
- **Active Agent:** Sentinel.

### Lane 3: Reactive UX & Client Portals (Palette)
- **Primary Scope:** `commingle-swarm/web/`, `palette.md` journal.
- **Core Guardrails:**
  - Frontend components MUST be lit-html factory closures accepting a `reRender` callback.
  - Asynchronous client-portal tasks MUST be deferred using `setTimeout` to ensure parent rendering completed instantiation first.
  - Strictly use `pnpm` (`pnpm --filter=commingle-swarm-web run build/serve`); Node-bound files MUST never use npm or yarn.
  - Keep UX code modifications minimal (under 50 lines) to avoid regression.
- **Active Agent:** Palette.

### Lane 4: Multi-Agent Team-Orchestration (MoneyBall / Mail)
- **Primary Scope:** `termux-multi-agent/src/team_manager.py`, `roster.json`, `.github/actions/mcp-agent-mail/`.
- **Core Guardrails:**
  - Dynamic roster management MUST employ ELO/3L0 calculations, spectator betting simulations, and culling/mutating bottom/top percentages.
  - Agent Mail relies on the Rust-based composite action mailbox under `.github/actions/mcp-agent-mail/action.yml`.
- **Active Agent:** MoneyBall Scout / Betting Arena.

### Lane 5: Peer Routing, Context, & Workflows (Grok / Jules)
- **Primary Scope:** `scripts/model_router.py`, `agent-review-auto-jules.yml`, `peer-review-orchestrator.yml`, `agent-continuous-ops.yml`.
- **Core Guardrails:**
  - To prevent import-time crashes on environments lacking `rich` or third-party curl binaries (e.g., Termux NDK), CLI entrypoints MUST wrap checks in try-except fallbacks, and tests MUST handle gracefully.
  - Fallbacks for `curl_cffi` MUST override requests `__init__` and strip out custom `impersonate` keyword arguments.
  - Programmatic Jules runs use stable context keys (`pr-<number>-<branch>`) loaded/saved via `.github/actions/agent-context-store`.
  - Enforce dual-quota capacities (3 concurrent active runs, 15 runs per rolling 24-hour period).
- **Active Agent:** Grok / Jules.

---

## 5. Dual-Gate Spine: The Non-Negotiable Integration Rules

No PR may merge to `master-staging` (and ultimately promote to `master`) without passing the two-gate spine checks:

1. **Repo Gate:** `python3 scripts/ci/repo_gate.py` (Validates ast structural invariants, file exclusions, and syntax).
2. **Termux Smoke Gate:** `python3 scripts/ci/termux_smoke.py` (Verifies script launches, fallback routines, and command line options in headless simulation).

For offline-first on-device execution (like BLU B160V mobile devices), execution is strictly limited to standard-library Python scripts. Heavy runtimes (Rust, Bun, Node) are cloud-side offloads only.

---

## 6. Verification and Maintenance Checklist

To maintain this SSOT, automated sweeps (2-hour cron) and manual operator audits will check:
- [x] Timing quotas are aligned with the elevated budgets in `model_router.py`.
- [x] Cooldown policies prevent concurrent write-clashes on files.
- [x] Security permissions remain tightly bound to Sentinel standards.
- [x] Branch scope is clear and contains no class 3/4 leaked credentials.

---

*Consolidated & Approved by Grok Orchestration Engine (xAI) on behalf of the Termux Monorepo Operators, 2026.*
