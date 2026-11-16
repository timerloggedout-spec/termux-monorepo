# ArchW1z Gate Spine

> **Status:** LIVE
> **Branches:** `master-staging` (hygiene) · `termux-smoke` (runtime surface)

## Two gates, one constitution

```text
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
| ICM impact receipt | exact pull-request delta + primary cards + related updates | HARD |
| Debt counters | whole index | RATCHET |

The ICM impact validator runs as a distinct named job (`ICM impact gate`) in the repo-gate workflow on every pull request. Exactly one changed `docs/icm/changes/*.json` receipt must enumerate the complete PR delta, identify existing primary ICM cards, and list related repository records changed in the PR. A receipt may declare `updated` only when at least one primary ICM card is changed; `no-map-change` requires a non-empty rationale. Missing, stale, incomplete, unsafe, or unsupported receipt fields fail closed.

### Merge protection

Branch protection must require the exact status check `ICM impact gate` for `master`. The active repository ruleset inspected on 2026-11-16 (`master-no-rewind`) enforces deletion and non-fast-forward protection only; it does **not** require status checks. The ICM validator is implemented as a CI check, but merge blocking is not established until this required-check rule is configured and verified.

### Tests

```bash
python3 -B -m unittest discover -s tests -p 'test_icm_impact_gate.py' -v
python3 scripts/ci/icm_impact_gate.py --base origin/master
```

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

```text
P0  credential / session-store containment
    repo-gate (including ICM impact receipt)
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

1. Branch off `master` or the active integration branch.
2. Add the ICM impact receipt before opening the PR.
3. Smallest atomic change that preserves invariants.
4. Push → repo-gate (including ICM impact) and termux-smoke run on the PR.
5. Green on both + verified task outcome → candidate for `master`.

Do **not** treat `master` as the integration point for large TER-*
branches.

## Next ratchet targets

- `tracked_session_artifacts` → 0
- `tracked_browser_credential_stores` → 0
- `tracked_browser_profile_files` → 0
- `tracked_backup_files` → 0
- Reduce `device_absolute_symlinks`
