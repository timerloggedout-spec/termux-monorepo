# Lane-matrix recursive sweep

**Workflow:** `.github/workflows/ops-lane-matrix-sweep.yml`  
**Script:** `scripts/ops/lane_matrix_sweep.py`  
**Artifacts:** `docs/ops/generated/lane-matrix-status.json` + `.md`  
**Schedule:** `11 */6 * * *` (every 6 hours) + `workflow_dispatch`

## What it does

1. Lists all open PRs (paginated).
2. Age-buckets: ancient (≥40d) / stale (20–39) / mid (7–19) / fresh (≤6).
3. Classifies lanes: `WAIT` | `HOLD` | `EXTRACT` | `OBSERVE` (never auto-PROMOTE).
4. Writes generated status files and optionally commits them to `master`.
5. Posts a **debounced** thin pulse on issue **#175** (11h marker).

## What it does *not* do

- Merge, close, rebase, force-push, or label-spam.
- Treat age or file-count as a promote signal.
- Replace dual-gate (`hygiene+portability` + `termux_smoke`).

## Complements

| Workflow | Role |
|----------|------|
| `agent-continuous-ops.yml` | Jules / agent nudge |
| `merge-promotion-queue.yml` | Dual-gate candidate inventory (observer) |
| `agent-ecc-tools-ops.yml` `matrix-cycle` | ECC Tools only on #175 |
| **This sweep** | Age + lane inventory + #175 progress pulse |

## Manual run

```bash
# Actions → Lane matrix recursive sweep → Run workflow
# or:
python3 scripts/ops/lane_matrix_sweep.py --comment-175
```

Agent-Identity: Grok (Administrator)
