---
name: issue-175-matrix
description: OPERATOR priority matrix for timerloggedout-spec/termux-monorepo Issue #175. Triggers on priority matrix, master functional gate, operator continue, BIUDL, or maximize actions.
---

# Skill: issue-175-matrix

Catalog: `docs/ops/ISSUE-175-MATRIX.yaml`  
Validate: `python3 scripts/ml/validate_matrix.py`

## Hard rules (still in force)

1. No force-push to master.
2. Prefer small green rebased PRs.
3. Dual gates: `repo_gate.py` + `termux_smoke.py`.
4. Reject Class 3/4 artifacts.
5. GitLab / Vercel rate-limit are non-blocking.
6. Maximize Actions; skip-reason comments on quota.
7. Jules continue-only + durable context_key.
8. Large dirty PRs → extract-only (never wholesale).
9. Reviewer-noise / provider-state is not task failure.

## Live P0 (refresh each cycle)

| Item | Status |
|---|---|
| Master functional gate | LIVE / GREEN on dual-gate (`eefc068` terminal) |
| ML pipelines extract onto `c082f533` (supersedes dirty #549/#432) | OPEN / this PR |
| Catalog freshness (Historical Eval 35356132030) | EXTRA-RED / regenerating |
| SHE (#294) | OPEN |
| Actions hygiene (#268) | MONITOR |
| Historical backfill (#522 / HOLD #523 #527) | HOLD |
| Reviewer-noise taxonomy (#390 specimen, #546 landed) | LIVE |
| Manus / providers (#265) | HOT / parked restore |

Identity every disposition: `Agent-Identity: Grok (Administrator)`.
