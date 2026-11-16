# Codespace Lanes (Parallel Agent-Role Configs)

**Status:** live on `codespaces-multi-lane-agent-roles`  
**Target:** right-sized, purpose-built environments per agent-role taxonomy.

## Why this exists

VS Code and GitHub Codespaces support multiple devcontainer configurations per repository via `.devcontainer/<name>/devcontainer.json`. Instead of forcing every agent and collaborator into a single heavy container, this repository now ships **5 parallel lanes** mapped directly to the role load matrix defined in [docs/ops/SKILLS-INVENTORY.md](SKILLS-INVENTORY.md).

This extends, rather than replaces, the production agent lane established in #530/#531 (see [docs/ops/CODESPACE-AGENT-LANE.md](CODESPACE-AGENT-LANE.md) for that lane's full operator card).

## Parallel Lanes Matrix

| Lane | Path | Base Image | Role (SKILLS-INVENTORY.md) | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **BASH/Ops Agent (default)** | `.devcontainer/devcontainer.json` | `python:1-3.12-bullseye` | Admin / Grok Administrator | Unattended agent BASH lane, full toolchain (Python/Node/Rust/gh), production/dual-gate capable. Established in #499/#530/#531 — unchanged. |
| **Docs / Mintlify** | `.devcontainer/docs-lane/devcontainer.json` | `javascript-node:20-bullseye` | Discovery / Docs | Lightweight, fast build, Node + Mintlify CLI only. No Python/Rust/apt-heavy tooling, no `setup.sh`, no submodule init. |
| **PR-Triage / Governance** | `.devcontainer/governance-lane/devcontainer.json` | `base:bullseye` | Governance / proposal | git/gh CLI heavy, provenance-checking tools; prints a reminder to load `termux-monorepo-agentic-governance` + `docs/CONSENSUS.md` + `docs/proposals/AGENTIC-PERMISSIONS.md` on start. |
| **General Dev/Build** | `.devcontainer/general-dev/devcontainer.json` | `python:1-3.12-bullseye` | Collaborator / Codespace agent | Full monorepo code stack (same toolchain as default lane) plus a startup check of the dual-gate helpers (`scripts/ci/repo_gate.py`, `scripts/ci/termux_smoke.py`) so the lane is build/test-ready immediately. |
| **Oracle** | `.devcontainer/oracle/devcontainer.json` | `python:1-3.12-bullseye` | Evaluator | Tooled for judging *other* agents' work, not authoring it: `scripts/ci/oracle_watch.sh` runs the adaptive-wait WAIT→WATCH→VALIDATE→RE-FETCH→COMPARE→CLASSIFY→RECORD→REPEAT loop against a PR's CI check runs, plus a lightweight commit/trailer provenance check. Prints reminders to load `blind-agent-evaluation`, `multivariate-doe`, `pr-evidence-evaluation`, `mvt-experiment`, and `adaptive-wait` on start. |

## The Oracle (Evaluator lane persona)

The Evaluator lane's persona is named **Oracle**, following this org's existing agent-persona naming convention (see [`harmony_hub/config/GRIMOIRE_DICTIONARY.md`](../../harmony_hub/config/GRIMOIRE_DICTIONARY.md) — Chronomancer, Linguist, Bidder, Scout, Harvester). "Oracle" is evocative of watch/scry/judge, matching this lane's purpose: it evaluates and classifies other agents' PRs rather than producing its own changes. The **documented role-matrix mapping stays "Evaluator"** throughout this doc and `SKILLS-INVENTORY.md` for traceability — "Oracle" is the in-repo directory name and runtime persona only.

Its core tool, [`scripts/ci/oracle_watch.sh`](../../scripts/ci/oracle_watch.sh), is a standalone script (also usable outside Codespaces) that:

1. **CAPTURE**s the target PR's head SHA, title, and expected effect (all required checks green + mergeable).
2. Runs a lightweight **provenance/trailer check** on the PR's commits (flags short/boilerplate commit bodies — a nod to this org's Manus/Jules trailer-verification methodology, not a full re-implementation of it).
3. Loops **WAIT → WATCH → VALIDATE → COMPARE → CLASSIFY → RECORD** per the [`adaptive-wait`](../../.agents/skills/adaptive-wait/SKILL.md) skill's stall classes (admission/queue/execution), never treating `queued`/`in_progress` as terminal.
4. Exits with a distinct code per verdict (`0`=PASS, `1`=FAIL, `2`=STALLED, `3`=TIMEOUT) and prints an "Oracle verdict:" line suitable for pasting into a PR review comment.

## Skill loading per lane

Every lane's `postCreateCommand` now prints a `[skills]` line naming its `docs/ops/SKILLS-INVENTORY.md` **Role load matrix** row (Admin / Collaborator / Evaluator / Governance / Discovery) and a same-session convenience snapshot of that row's current skills. The instruction is a **role-lookup**, not a pinned value: `SKILLS-INVENTORY.md` states its own version/SHA and changes frequently, so the authoritative source is always that file's live table for the printed role — the snapshot is a courtesy, not a substitute for checking it.

| Lane | Role row in SKILLS-INVENTORY.md | Load first | Then | Optional |
|---|---|---|---|---|
| BASH/Ops Agent (default) | Admin / Grok Administrator | `evidence-led-monorepo-ops` + `adaptive-wait` | `termux-monorepo-agentic-governance` + `review-loop` | `adaptive-feedback-cycle`, `production-reconciliation` |
| Docs / Mintlify | Discovery / extend | `find-skills` | skills.sh leaderboard + this inventory | — |
| PR-Triage / Governance | Governance / proposal | `termux-monorepo-agentic-governance` | `docs/CONSENSUS.md` + `docs/proposals/AGENTIC-PERMISSIONS.md` | `review-loop` |
| General Dev/Build | Collaborator / Codespace agent | `adaptive-feedback-cycle` | dual-gate (`repo_gate` + `termux_smoke`) + conventions | `review-loop` |
| Oracle | Evaluator | `blind-agent-evaluation` + `multivariate-doe` | `pr-evidence-evaluation` + `mvt-experiment` | `evidence-envelope` |

*(This table mirrors `SKILLS-INVENTORY.md`'s Role load matrix at time of writing. If the two ever disagree, `SKILLS-INVENTORY.md` is the source of truth — update this row in the same PR that changes the matrix, per its own "Single navigation SSOT" rule.)*

## Create a Codespace on a specific lane

1. Navigate to the repository on GitHub.
2. Click the green **Code** button.
3. Select the **Codespaces** tab.
4. Click the **"..."** (More options) button next to the "+" icon, and select **"New with options..."**.
5. Under **Dev container configuration**, select the desired lane by its name (e.g., `termux-monorepo-docs-lane`, `termux-monorepo-governance-lane`, or `termux-monorepo-general-dev-lane`).
6. Click **Create codespace**.

*Note: Clicking the plain "+" or "Create codespace on master" button will spin up the default root config (BASH/Ops Agent lane) unchanged.*

## Not yet covered

The [docs/ops/SKILLS-INVENTORY.md](SKILLS-INVENTORY.md) role matrix also lists an **Evaluator** role (which loads `blind-agent-evaluation`, `pr-evidence-evaluation`, and `mvt-experiment`). A dedicated lane for Evaluators is not yet implemented and remains a planned follow-up.

## Boundaries

- **Environment Only:** These lanes are environment and tooling presets only. They do not change repository permissions.
- **Governance Grounding:** Every lane is strictly bound by [docs/proposals/AGENTIC-PERMISSIONS.md](../proposals/AGENTIC-PERMISSIONS.md) and the 5-tier consensus model in [docs/CONSENSUS.md](../CONSENSUS.md). Tier 4 operations (credential rotation, force-push, history rewrite, branch-protection changes) remain human-only regardless of the lane being used.
- **Adding Lanes:** To add a new lane, create `.devcontainer/<name>/devcontainer.json` and add a corresponding row to the table above in the same PR.

---
Implements: codespaces-multi-lane-agent-roles · extends codespace-agent-lane (#530/#531)