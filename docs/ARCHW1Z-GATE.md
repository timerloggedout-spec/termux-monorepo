# ArchW1z Gate Spine

> **Status:** LIVE
> **Canonical integration branch:** `master`
> **Validation model:** repository baseline + scope-specific runtime/domain gates

## Gate ownership

```
all repository changes
       │
       ▼
repo-gate
       │
       ├── Termux runtime / Android device changes ──► termux-smoke
       │
       ├── provider changes ─────────────────────────► provider contracts
       │
       ├── application changes ──────────────────────► application tests
       │
       └── workflow changes ─────────────────────────► workflow contracts
       │
       ▼
master
```

`repo-gate` is the general hygiene, portability, secrets, and debt-ratchet gate.

`termux-smoke` validates Termux runtime and device operations. Apply it when the changed workstream targets Android/Termux execution, Termux entrypoints, Termux device integrations, or Termux operational flows.

## Gate 1 — repo-gate (repository-wide)

```bash
python3 scripts/ci/repo_gate.py
```

Workflow: `.github/workflows/repo-gate.yml`

### Design rules

- **stdlib only** — Python standard library execution with local repository inputs
- **index-based** — reads `git ls-files` as the canonical change index
- **device-friendly** — same command works on Termux and in CI
- **HARD checks** scoped to changed files
- **RATCHET** on whole-repository debt counters

### Enforced checks

| Check | Scope | Failure mode |
|---|---|---|
| Python / shell / JSON syntax | changed files | HARD |
| Portable symlinks | changed symlinks | HARD |
| Session artifacts | changed paths | HARD |
| Browser credential stores | changed paths | HARD |
| Committed backups | changed paths | HARD |
| High-confidence secrets | changed content | HARD |
| Debt counters | whole index | RATCHET |

Baseline: `scripts/ci/baseline.json`

## Gate 2 — termux-smoke (Termux scope only)

```bash
python3 scripts/ci/termux_smoke.py
python3 scripts/ci/termux_smoke.py --with-optional
python3 scripts/ci/termux_smoke.py --json
```

Workflow: `.github/workflows/termux-smoke.yml`
Full docs: [`docs/TERMUX-SMOKE.md`](TERMUX-SMOKE.md)

### Required checks

- Python ≥ 3.9
- Termux smoke entrypoints and supporting repository paths present
- repo-gate and smoke scripts compile
- git on PATH
- bash on PATH on Termux; soft elsewhere
- writable TMPDIR

### Optional Termux-facing probes

- deepcli / multi-ai launcher compile
- ArchWiz Termux sample modules compile
- termux-api presence note
- connector and device-surface probes registered by the Termux smoke suite

The workflow uses path filters for Termux-owned surfaces. General repository, provider, quota, and application contracts run in their owning workflows.

## Domain gates

| Scope | Owning validation |
|---|---|
| Repository hygiene / portability | `repo-gate` |
| Termux runtime / Android device | `termux-smoke` |
| Bucket headroom | `bucket-headroom-contract` + watcher workflow |
| Provider adapters | provider contract suite |
| Application components | owning application tests |
| Workflow contracts | owning workflow contract suite |

## Integration order

1. Select the owning proposal item and changed subsystem.
2. Run `repo-gate` on the candidate SHA.
3. Run `termux-smoke` when the workstream is Termux-related.
4. Run each required domain-specific test suite.
5. Re-fetch current-head checks and inspect actual outputs.
6. Promote when all required scope gates pass and the task outcome is verified.

## Landing work

- Branch from current `master`.
- Keep each change within its registered work item.
- Cite `Implements: <ITEM-ID>` in the PR and commit context.
- Preserve source refs during extraction and record exact SHAs.
- Validate the candidate SHA against its required scope gates.
