# ArchW1z Gate Spine

> **Status:** LIVE
> **Workflow triggers (verified 2026-11-15):** both gates run on pull requests; repo-gate also runs on pushes to `master` and `master-staging`; termux-smoke runs on pushes to `master`, `master-staging`, and `termux-smoke`. See the workflow YAML for the executable trigger contract.

## Two gates, one constitution

```
repo-gate          hygiene / portability / secrets / ratchet
       ↓
termux-smoke       agent runtime surface is alive
       ↓
language / provider gates (later)
       ↓
master
```

Every change that wants to reach `master` should survive both gates.

---

## Gate 1 — repo-gate

```bash
python3 scripts/ci/repo_gate.py
```

Workflow: `.github/workflows/repo-gate.yml`
Docs: this file + original Critical-Eval recommendation

### Design rules (non-negotiable)

- **stdlib only** — no pip, no cargo, no node, no network
- **index-based** — reads `git ls-files`, never the working tree
- **device-friendly** — same command works on Termux and in CI
- **HARD checks** scoped to *changed* files
- **RATCHET** on whole-repo debt counters (debt may only shrink)

### What it enforces

| Check | Scope | Failure mode |
|-------|-------|--------------|
| Python / shell / JSON syntax | changed files | HARD |
| Portable symlinks | changed symlinks | HARD |
| No new session artifacts | changed paths | HARD |
| No browser credential stores | changed paths | HARD |
| No committed backups | changed paths | HARD |
| High-confidence secrets | changed content | HARD |
| Debt counters | whole index | RATCHET |

Baseline: `scripts/ci/baseline.json`
Lower debt with: `python3 scripts/ci/repo_gate.py --write-baseline`

---

## Gate 2 — termux-smoke

```bash
python3 scripts/ci/termux_smoke.py
python3 scripts/ci/termux_smoke.py --with-optional   # agent surfaces
python3 scripts/ci/termux_smoke.py --json            # for agents
```

Workflow: `.github/workflows/termux-smoke.yml`
Full docs: [`docs/TERMUX-SMOKE.md`](TERMUX-SMOKE.md)

### What it enforces (required)

- Python ≥ 3.9
- Gate scripts present and compile
- git on PATH
- bash on Termux (soft elsewhere)
- writable TMPDIR

### Optional probes (`--with-optional`)

- deepcli / multi-ai launcher compile (no network)
- archwiz sample modules compile
- termux-api presence note

---

## Integration order (ArchW1z)

```
P0  credential / session-store containment
    repo-gate
    termux-smoke          ← now live
    deterministic configuration
    session SSOT schema

P1  dispatch event boundary
    DeepForge launcher resolver
    provider capability contract
    content-addressed index correctness

P2  DeepForge ↔ Rust protocol
    MCP
    harvesting / search expansion
    multi-provider parity
```

## How to land work

1. Read root `CLAUDE.md` and current `docs/ops/LANE-MATRIX.md` before selecting a base.
2. Branch from live `master` unless an active lane explicitly requires `master-staging` or another named integration branch.
3. Smallest atomic change that preserves invariants; open/update the PR against the lane-authorized base.
4. Both gate workflows run on pull requests; verify named jobs on the exact candidate SHA.
5. Green gates plus verified task outcome and mergeability authorize promotion under current policy.

Do **not** treat `master` as the integration point for large TER-*
branches.

## Next ratchet targets

- `tracked_session_artifacts` → 0
- `tracked_browser_credential_stores` → 0
- `tracked_browser_profile_files` → 0
- `tracked_backup_files` → 0
- Reduce `device_absolute_symlinks`


## Current-source note

This document describes gate commands and test intent. Exact workflow triggers are owned by `.github/workflows/repo-gate.yml` and `.github/workflows/termux-smoke.yml`; PR disposition/promotion rules are owned by the current `docs/ops/LANE-MATRIX.md` and root `CLAUDE.md`. Do not infer that either gate is restricted to a single branch from this document's historical branch names.
