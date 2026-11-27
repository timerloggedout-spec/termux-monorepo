# ArchW1z Gate Spine

> **Status:** LIVE  
> **Branches:** `master-staging` (hygiene lane) · `termux-smoke` (runtime lane)

## One universal floor, one conditional runtime gate

```text
every pull request / integration push
          │
          ▼
      repo-gate ─────────────── universal hygiene / portability / secrets / ratchet
          │
          ▼
   surface admission
      ├── Termux smoke ─────── Termux execution paths or manual dispatch
      ├── dangle census ────── reference-bearing source/target roots
      ├── Vercel ───────────── project path + affected-project + quota policy
      └── Devin ────────────── optional bounded worker with verified capacity
          │
          ▼
Siglary validation + applicable evidence on exact candidate SHA
          │
          ▼
        master
```

The repository gate is universal. Termux smoke is conditional on the changed execution surface. The workflow check remains visible; its smoke steps execute when `scripts/ci/gate_admission.py` returns `required=true`.

## Gate 1 — repo-gate + Siglary

```bash
python3 scripts/ci/repo_gate.py
python3 scripts/ci/validate_siglary_mandate.py --base origin/master
```

Workflow: `.github/workflows/repo-gate.yml`

### Design rules

- **stdlib only** — Python standard library, shell, and Git.
- **index-based** — read `git ls-files`, then validate changed paths.
- **device-friendly** — same command on Termux and CI.
- **HARD checks** scoped to changed files.
- **RATCHET** on whole-repository debt counters; debt trends toward zero.

### Enforcement

| Check | Scope | Result |
|---|---|---|
| Python / shell / JSON syntax | changed files | HARD |
| Portable symlinks | changed symlinks | HARD |
| Session artifacts | changed paths | HARD |
| Browser credential stores | changed paths | HARD |
| Committed backups | changed paths | HARD |
| High-confidence secrets | changed content | HARD |
| Debt counters | whole index | RATCHET |

Baseline: `scripts/ci/baseline.json`  
Debt review: `python3 scripts/ci/repo_gate.py --write-baseline`

## Gate 2 — Termux runtime smoke

```bash
python3 scripts/ci/termux_smoke.py
python3 scripts/ci/termux_smoke.py --with-optional
python3 scripts/ci/termux_smoke.py --json
```

Workflow: `.github/workflows/termux-smoke.yml`  
Admission helper: `scripts/ci/gate_admission.py`  
Full guide: [TERMUX-SMOKE.md](TERMUX-SMOKE.md)

### Admission contract

- A matching Termux path admits core smoke, regression tests, and optional agent probes.
- Manual `workflow_dispatch` admits smoke.
- Missing base/head or diff evidence admits smoke.
- A complete path list with no Termux surface match records `SKIPPED` with reason `Termux surface unchanged`.
- The PR lane classifier consumes the same path predicate and records `termux_smoke_required` independently from check-run status.

The bucket-headroom PyYAML/pytest suite runs through its own path-scoped workflow: `.github/workflows/bucket-headroom-contract.yml`.

### Runtime contract

| Check | Requirement |
|---|---|
| Python ≥ 3.9 | required |
| Gate scripts present and compile | required |
| git on PATH | required |
| bash on Termux | required |
| writable TMPDIR | required |
| deepcli / multi-ai launcher compile | optional |
| archwiz sample modules compile | optional |
| termux-api presence | observation |

## Reference and provider lanes

### Dangle census

`scripts/ci/dangle_check.py` retains the current baseline ratchet and finding scopes `.github/` + `apps/`. Pull-request admission also covers target roots such as `docs/`, `scripts/`, `ops/`, `config/`, `workspace/`, `archwiz/`, `.agents/`, and `tests/`.

### Vercel

The linked `historical-corpus-explorer` project uses `apps/historical-corpus-explorer` as its root, affected-project deployment filtering, and a project-scoped ignore command. Its 2026-11-27 quota incident and provider verification state are recorded in [DEPLOYMENT-LANES.md](ops/DEPLOYMENT-LANES.md).

### Devin

Devin remains an optional bounded worker. Admission uses current API eligibility, available free quota, billing boundary, task fit, and explicit referral-credit provenance. The 2026-11-27 operator report is recorded as a lead pending provider/account evidence.

## Integration order

```text
P0  credential / session-store containment
    repo-gate
    Siglary validation
    Termux smoke when the surface classifier admits it
    deterministic configuration
    session SSOT schema

P1  dispatch event boundary
    DeepForge launcher resolver
    provider capability contract
    content-addressed index correctness
    dangle target-path validation

P2  DeepForge ↔ Rust protocol
    MCP
    harvesting / search expansion
    multi-provider parity
```

## Promotion contract

1. Run repo-gate on every candidate.
2. Run Siglary validation on the exact candidate SHA.
3. Run Termux smoke when the shared classifier admits the Termux surface; record `SKIPPED` with reason for other slices.
4. Run reference and provider lanes when their admission conditions match.
5. Promote when every applicable required gate passes on the same immutable SHA and the task outcome is verified.

Use small atomic changes. Target `master` for integration work; use the active staging lane when the proposal names it.
