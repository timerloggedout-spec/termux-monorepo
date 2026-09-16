# Termux-Monorepo Audit Findings

## System Overview
- **Core Stack:** Agentic development environment for Termux/CI.
- **Key Projects:** `deepcli`, `archwiz`, `termux-multi-agent`, `cli-synthegration`, `llm_map`.
- **Architecture:** "Four-plane" model with an event-sourced dispatch pipeline.
- **CI/CD:** Two-gate spine (`repo-gate.py` for hygiene, `termux-smoke.py` for runtime).
- **Branching:** `master-staging` is the integration spine; `master` is for stable, green releases.

## Branch & PR Evaluation
- **master-staging:** The current integration target.
- **PR #11 (termux-smoke):** Merged, adds the second gate.
- **PR #6 (TER-9):** "NO-GO" wholesale due to provider abstraction failures and bugs, but contains useful patches.
- **PR #3 (Security):** Incomplete; removes session stores from tip but lacks history remediation and credential rotation.
- **PR #2 (Rust CI):** Parked; invalid Python in heredoc and wrong abstraction level (should be post-repo-gate).
- **PR #5 (Dispatch Log):** Needs decoupling of cache-save from dispatch-pipeline to avoid recursion/latency.

## Codebase Audit
- **archwiz/config.py:** Correct environment-aware config (termux/replit/local).
- **archwiz/archwiz.py:** Dashboard with hardcoded `~/archwiz/` paths that need replacing with `config.py` constants.
- **deepcli/deepcli/core.py:** Contains silent `except: pass` in dispatch hooks and SSE parsing.
- **workspace/llm_map/:** The "engine room" with AST indexing, task runners, and agent orchestration logic.
- **workspace/CAVEMAN_INDEX.md:** High-level orientation for the ecosystem.

## Novel Work Proposal: Linear Integration
- **Context:** User states "Linear is integrated", but no code uses it yet.
- **Goal:** Bridge `master_tasks.json` and `taDone.md` to Linear issues.
- **Implementation:** Create `archwiz/linear_sync.py` to sync local task status to Linear.

## Action Plan for Manus
1. Branch from `master-staging`.
2. Fix `archwiz/archwiz.py` to use `archwiz.config`.
3. Implement `archwiz/linear_sync.py`.
4. Add Linear Sync option to `archwiz.py` menu.
5. Extract/Fix silent `except: pass` in `deepcli/deepcli/core.py` (logging to `LOG_DIR`).
