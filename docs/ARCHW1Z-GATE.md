# ArchW1z Gate Spine

> **Status:** LIVE
> **Branches:** `master-staging` (hygiene) · `termux-smoke` (runtime surface)

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

## Gate 1 — repo-gate (on `master-staging`)

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

## Gate 2 — termux-smoke (on `termux-smoke`)

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

1. Branch off `master-staging` or `termux-smoke`.
2. Smallest atomic change that preserves invariants.
3. Push → both gates run on PR.
4. Green on both → candidate for `master`.

Do **not** treat `master` as the integration point for large TER-*
branches.

## Next ratchet targets

- `tracked_session_artifacts` → 0
- `tracked_browser_credential_stores` → 0
- `tracked_browser_profile_files` → 0
- `tracked_backup_files` → 0
- Reduce `device_absolute_symlinks`
