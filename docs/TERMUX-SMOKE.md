# Termux Smoke Gate — Agentic runtime surface

> **Branch:** `termux-smoke`
> **Script:** `scripts/ci/termux_smoke.py`
> **Workflow:** `.github/workflows/termux-smoke.yml`

## Position in the spine

```
repo-gate          (hygiene / portability / secrets / ratchet)
       ↓
termux-smoke       (agent runtime surface is alive)   ← you are here
       ↓
language gates     (python / shell / rust — later)
       ↓
provider tests     (deepcli / multi-ai — later)
       ↓
Termux device CI   (optional self-hosted / manual)
```

## Why a dedicated branch + gate

Agents (DeepCLI, ArchWiz, multi-ai, MCP, Devin-style workers) assume a
minimum living surface:

- Python ≥ 3.9
- git on PATH (index-based gates)
- bash available on real Termux
- writable temp
- gate scripts themselves compile
- optional: deepcli / archwiz trees compile without executing network code

This is **not** a full integration test suite. It is a fast, deterministic
"is the cockpit even powering on?" check that works on-device and in CI.

## How to run

```bash
# Core (required) — stdlib only, no network
python3 scripts/ci/termux_smoke.py

# Also probe agent surfaces (still no network)
python3 scripts/ci/termux_smoke.py --with-optional

# Machine-readable for agent parsers
python3 scripts/ci/termux_smoke.py --json --with-optional

# Treat optional failures as hard
python3 scripts/ci/termux_smoke.py --with-optional --strict
```

## What it checks

| Check | Required | Notes |
|-------|----------|-------|
| python-version ≥ 3.9 | yes | |
| repo-layout (gate scripts + docs) | yes | |
| repo-gate compiles | yes | |
| smoke self-compiles | yes | |
| git on PATH | yes | needed by repo-gate |
| bash on PATH | yes on Termux, soft elsewhere | |
| writable TMPDIR | yes | |
| deepcli / multi-ai launcher compile | optional | `--with-optional` |
| archwiz sample modules compile | optional | `--with-optional` |
| termux-api presence note | optional note | never required |

## Branch usage

- **`termux-smoke`** — development and iteration of the smoke gate itself.
- Promote green smoke changes into **`master-staging`** (which already has
  the hygiene gate).
- Only after both gates are green should changes become candidates for
  **`master`**.

## Agentic integration notes

- Agents should prefer `--json` output and treat `ok: false` as a hard stop
  before attempting provider or harvest work.
- Do **not** add network calls, API keys, or browser launches to the core
  path. Optional probes must remain compile/help-only.
- Future expansion (still cheap): presence of `deepcli` console entrypoint,
  `archwiz` health command, MCP config schema validation — all offline.

## Relationship to ChatGPT Critical-Eval

This implements the "Termux smoke tests" layer that the Critical-Eval
placed *after* the cheap repo-gate and *before* provider/Rust work in the
proposed CI ladder.
