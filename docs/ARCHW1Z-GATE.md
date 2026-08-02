# ArchW1z Gate — master-staging as check spine

> **Status:** LIVE on `master-staging`  
> **Invariant set:** P0 hygiene + portability + credential containment

## What changed

`master-staging` is no longer a redundant identical copy of `master`.

It is now the **check gate**.

Every change that wants to reach `master` should first land on (or be
merged through) `master-staging` and survive the repo-gate.

## The gate itself

```
python3 scripts/ci/repo_gate.py
```

or automatically via `.github/workflows/repo-gate.yml` on every PR and
every push to `master` / `master-staging`.

### Design rules (non-negotiable)

- **stdlib only** — no pip, no cargo, no node, no network
- **index-based** — reads `git ls-files`, never the working tree
- **device-friendly** — same command works on Termux and in CI
- **HARD checks** scoped to *changed* files (so historical debt does not
  block unrelated PRs)
- **RATCHET** on whole-repo debt counters (debt may only shrink)

### What it currently enforces

| Check | Scope | Failure mode |
|-------|-------|--------------|
| Python syntax | changed `.py` | HARD |
| Shell syntax (`bash -n`) | changed `.sh` | HARD |
| JSON parse | changed `.json` | HARD |
| Portable symlinks | changed symlinks | HARD (device-absolute / absolute targets) |
| No new session artifacts | changed paths | HARD (`.deepcli`, `.pi`, `.synthegration`, `session_store`) |
| No browser credential stores | changed paths | HARD |
| No committed backups | changed paths | HARD (`.bak` / `.old`) |
| High-confidence secrets | changed content | HARD |
| Debt counters | whole index | RATCHET (may only go down) |

### Baseline location

`scripts/ci/baseline.json`

Lower it when you clean debt:

```bash
python3 scripts/ci/repo_gate.py --write-baseline
```

## Integration order (ArchW1z)

```
P0  credential / session-store containment
    repo-gate  ← you are here
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

## How to use master-staging

1. Branch off `master-staging` (or open PR targeting it).
2. Make the smallest atomic change that preserves the invariants.
3. Push → gate runs automatically.
4. Only after green does the change become a candidate for `master`.

Do **not** treat `master` as the integration point for large TER-*
branches. The gate exists so that the overlapping truths collapse
instead of accumulating.

## Next ratchet targets (recommended)

- Drive `tracked_session_artifacts` → 0
- Drive `tracked_browser_credential_stores` → 0
- Drive `tracked_browser_profile_files` → 0
- Drive `tracked_backup_files` → 0
- Reduce `device_absolute_symlinks`

Each of those is a pure win for the ArchW1z constitution.
