# Codespace Agent Lane (Production)

**Status:** live on `master` via #530 (`94104904`).  
**Target:** unattended agent BASH + shared collaborator compute + dual-gate green path.

## Why this exists

| Role | Benefit |
|------|---------|
| **Agent (Grok / BASH lanes)** | Persistent Linux shell with `ARCHWIZ_ENV=codespace`, system Python, `gh`, Node 20, Rust, shallow submodules. No Termux device required for review, extract, gate, and PR work. |
| **Collaborators** | Same `.devcontainer` → identical toolchain. Create from `master` → Code → Codespaces. No special branch required. |
| **Production / dual gates** | Codespace can run `python3 scripts/ci/repo_gate.py` and `python3 scripts/ci/termux_smoke.py` (or the agentic smoke path) as a simulation/support plane. Evidence stays in PR checks; Codespace is the interactive/agent compute surface. |

Android/Termux remains the **target** execution environment. Codespace is support / simulation / agent plane only.

## Create (one-time)

1. Repo → **Code** → **Codespaces** → **Create codespace on `master`**.
2. Machine: default matches `hostRequirements` (4 CPU / 8 GB / 32 GB). Bump only if needed.
3. First start runs `postCreateCommand`: `setup.sh` (codespace path) + shallow submodule init.
4. Confirm:
   ```bash
   echo "$ARCHWIZ_ENV"          # → codespace
   python3 -c "from archwiz import config; print(config.ARCHWIZ_ENV)"
   python3 scripts/ci/repo_gate.py --help || true
   ```

## Agent operating rules (no HITL)

- Prefer **extract-only** small PRs; never wholesale dirty mega-PRs.
- Dual gates must stay green on `master` before merge.
- Secrets: use **Codespaces secrets** / Actions secrets only. Never paste tokens into chat, instructions, or committed files (see `docs/proposals/active/agentic-scoped-access/MANIFEST.md`).
- Collaborator Codespaces are separate instances; do not assume shared FS or shared session.

## Production loop (agent)

1. Create or reuse Codespace on `master` (or feature branch under review).
2. Branch → bounded change → local gate smoke → push → PR.
3. Wait for dual-gate checks; merge only when green/stable.
4. Leave evidence (PR body, check runs, short ops note if process changed).

## Boundaries

- Codespace is **not** a substitute for Termux device capability claims.
- Prebuilds / multi-repo permissions / extra secrets are optional follow-ups; empty `codespaces.repositories` is intentional until needed.
- This file is the operator card; do not duplicate long rationale into README.
- This is one of several parallel role-scoped lanes now shipped under `.devcontainer/`; see [`docs/ops/CODESPACE-LANES.md`](CODESPACE-LANES.md) for the full lane matrix (Docs/Mintlify, PR-Triage/Governance, General Dev/Build). This card stays the operator reference for the lane described above only.

Implements: codespace-agent-lane / #530 follow-on  
BIUDL.
