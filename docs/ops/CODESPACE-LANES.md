# Codespace Lanes (Parallel Agent-Role Configs)

**Status:** live on `codespaces-multi-lane-agent-roles`  
**Target:** right-sized, purpose-built environments per agent-role taxonomy.

## Why this exists

VS Code and GitHub Codespaces support multiple devcontainer configurations per repository via `.devcontainer/<name>/devcontainer.json`. Instead of forcing every agent and collaborator into a single heavy container, this repository now ships **4 parallel lanes** mapped directly to the role load matrix defined in [docs/ops/SKILLS-INVENTORY.md](SKILLS-INVENTORY.md).

This extends, rather than replaces, the production agent lane established in #530/#531 (see [docs/ops/CODESPACE-AGENT-LANE.md](CODESPACE-AGENT-LANE.md) for that lane's full operator card).

## Parallel Lanes Matrix

| Lane | Path | Base Image | Role (SKILLS-INVENTORY.md) | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **BASH/Ops Agent (default)** | `.devcontainer/devcontainer.json` | `python:1-3.12-bullseye` | Admin / Grok Administrator | Unattended agent BASH lane, full toolchain (Python/Node/Rust/gh), production/dual-gate capable. Established in #499/#530/#531 — unchanged. |
| **Docs / Mintlify** | `.devcontainer/docs-lane/devcontainer.json` | `javascript-node:20-bullseye` | Discovery / Docs | Lightweight, fast build, Node + Mintlify CLI only. No Python/Rust/apt-heavy tooling, no `setup.sh`, no submodule init. |
| **PR-Triage / Governance** | `.devcontainer/governance-lane/devcontainer.json` | `base:bullseye` | Governance / proposal | git/gh CLI heavy, provenance-checking tools; prints a reminder to load `termux-monorepo-agentic-governance` + `docs/CONSENSUS.md` + `docs/proposals/AGENTIC-PERMISSIONS.md` on start. |
| **General Dev/Build** | `.devcontainer/general-dev/devcontainer.json` | `python:1-3.12-bullseye` | Collaborator / Codespace agent | Full monorepo code stack (same toolchain as default lane) plus a startup check of the dual-gate helpers (`scripts/ci/repo_gate.py`, `scripts/ci/termux_smoke.py`) so the lane is build/test-ready immediately. |

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