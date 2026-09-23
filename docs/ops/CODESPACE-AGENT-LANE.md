# Codespace Agent Lane (Production)

**Status:** live on `master` via #530 (`94104904`).  
**Target:** unattended agent BASH + shared collaborator compute + dual-gate green path.

## Why this exists

| Role | Benefit |
|------|---------|
| **Agent (Grok / BASH lanes)** | Persistent Linux shell with `ARCHWIZ_ENV=codespace`, system Python, `gh`, Node 20, Rust, shallow submodules. No Termux device required for review, extract, gate, and PR work. |
| **Collaborators** | Same `.devcontainer` → identical toolchain. Create from `master` → Code → Codespaces. No special branch required. |
| **Production / dual gates** | Codespace can run `python3 scripts/ci/repo_gate.py` and `python3 scripts/ci/termux_smoke.py` (or the agentic smoke path) as a simulation/support plane. Evidence stays in PR checks; Codespace is the interactive/agent compute surface. |
| **BIFROST-006** | Preferred host for mocker + Bifrost + Go benchmark smoke (see `docs/proposals/active/bifrost-gateway-integration/BENCHMARK-SMOKE.md`). |

Android/Termux remains the **target** execution environment. Codespace is support / simulation / agent plane only.

## Create paths

### A) UI (always available)

1. Repo → **Code** → **Codespaces** → **Create codespace on `master`**.
2. Machine: default matches `hostRequirements` (4 CPU / 8 GB / 32 GB). Bump only if needed.
3. First start runs `postCreateCommand`: `setup.sh` (codespace path) + shallow submodule init.
4. Confirm:
   ```bash
   echo "$ARCHWIZ_ENV"          # → codespace
   python3 -c "from archwiz import config; print(config.ARCHWIZ_ENV)"
   python3 scripts/ci/repo_gate.py --help || true
   ```

### B) API via workflow_dispatch (credential plane #184)

PATs listed on issue **#184** include `codespace` scope. The **value** must live only in repo secrets — never in the issue body or chat.

1. Settings → Secrets and variables → Actions → New repository secret:
   - Name: `CODESPACE_CREATE_TOKEN`
   - Value: a classic/fine-grained PAT with **codespace** (+ repo) scope from the #184 inventory
2. Actions → **Codespace create (dispatch)** → Run workflow
   - `ref`: `master` (or feature branch)
   - `machine`: `basicLinux32gb` (default)
   - `display_name`: e.g. `agent-bifrost-006`
3. Job summary prints codespace `name` + `web_url`

Workflow: `.github/workflows/codespace-create.yml`

Default `GITHUB_TOKEN` in Actions usually **cannot** create Codespaces; that is why a dedicated PAT secret is required.

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
- Prebuilds / multi-repo permissions / extra secrets are optional follow-ups; empty `codespaces.repositories` is intentional until needed. Prebuild cost decision lives in #500 / codespaces-enablement proposal — not auto-enabled here.
- This file is the operator card; do not duplicate long rationale into README.

Implements: codespace-agent-lane / #530 follow-on  
BIUDL.
