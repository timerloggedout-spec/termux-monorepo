# Migration: jules-ade → skyhook

## What was deleted

The entire **`jules-ade/`** tree on `feature/skyhook` after the rename. Nothing outside that package was removed.

### Files removed (all under `jules-ade/`)

| Path |
|------|
| `jules-ade/AGENTS.md` |
| `jules-ade/README.md` |
| `jules-ade/roster.yaml` |
| `jules-ade/bridge/__init__.py` |
| `jules-ade/bridge/config.py` |
| `jules-ade/bridge/dispatch.py` |
| `jules-ade/mcp/README.md` |
| `jules-ade/research/ANTIGRAVITY_SURFACE.md` |
| `jules-ade/research/JULES_SURFACE.md` |
| `jules-ade/research/SOURCES.md` |
| `jules-ade/scavenge/templates/README.md` |
| `jules-ade/scavenge/templates/antigravity-sdk/SOURCE.txt` |
| `jules-ade/scavenge/templates/jules-mcp/SOURCE.txt` |
| `jules-ade/scripts/doctor.py` |
| `jules-ade/tasks/README.md` |
| `jules-ade/tasks/queue/JULES-ADE-01-scaffold.yaml` |
| `jules-ade/tasks/queue/JULES-ADE-02-bridge-tests.yaml` |
| `jules-ade/tasks/queue/JULES-ADE-03-example-dispatch.yaml` |
| `jules-ade/tasks/queue/JULES-ADE-04-mcp-termux.yaml` |
| `jules-ade/tasks/queue/JULES-ADE-05-verify-private-forks.yaml` |

### What replaced it

**`skyhook/`** on branch **`feature/skyhook`** — same role, Jules-first, 🥇 fork RECON, Antigravity deferred.

Legacy ops docs still mention the old name:
- `docs/ops/JULES_ADE_PROJECT.md`
- `docs/ops/JULES_REPO_ROSTER.yaml`

Those remain on `master-staging` until a focused PR rewrites pointers to `skyhook/`.

### Branches / PRs

| Item | Status |
|------|--------|
| `feature/jules-ade` | Superseded; do not extend |
| PR #23 (jules-ade draft) | Closed |
| `feature/skyhook` | Active multi-agent branch |
| PR #24 | Draft → `master-staging` |
