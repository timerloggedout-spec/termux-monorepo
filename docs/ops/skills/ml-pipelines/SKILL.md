---
name: ml-pipelines
description: Observe-mode GitHub ML pipelines for termux-monorepo. Triggers on ML Pipelines, MoneyBall, Issue #213, Issue #175, commit analysis, leaderboard, provider attribution, or when an operator asks to keep ML pipelines.
---

# Skill: ml-pipelines

**Load path:** `.agents/skills/ml-pipelines/SKILL.md`  
**Human mirror:** `docs/ops/skills/ml-pipelines/SKILL.md`  
**Package:** `ml_pipelines/` (stdlib only)

Observe-mode scoring of PRs, issues, commits, and Actions. **Never** promote a MoneyBall score into a merge, secret, force-push, or issue-to-shell action. Dual gates (`repo_gate.py` + `termux_smoke.py`) still dominate.

## Run

```bash
python3 scripts/ml/validate_matrix.py
python3 scripts/ml/run_pipelines.py --snapshot ml_pipelines/fixtures/ops-snapshot.json
python3 -m unittest discover -s tests/ml_pipelines -p 'test_*.py'
```

## DAG

| Stage | Item | Authority |
|---|---|---|
| `issue_175_matrix` | MLP-02 | bind watch-list |
| `pr_minesweeper` | MLP-03 | dispositions only |
| `commit_analysis` | MLP-01 | prefix/author histogram |
| `actions_health` | MLP-01 | skip vs fail vs provider_state |
| `provider_attribution` | MLP-01 | bot vs shared-login |
| `lane_consolidation` | MLP-03 | drift flags |
| `moneyball_export` | MLP-01 | decision-support leaderboard |

## Hard fences

- No network in the package.
- No `token` / `secret` / `raw_body` / `prompt` fields in envelopes.
- `allow_write("merge")` is false.
- Dirty mega-PRs stay `DIRTY_HOLD` / `NO_GO` / `MEGA_REVIEW`.
- `not_executed` is never relabeled `execution_failure`.
- Vercel rate-limit, CodeRabbit review-rate-limit, Devin trial-expired → `provider_state` or `reviewer_noise`.

Complements: `evidence-led-monorepo-ops`, `review-loop`, `pr-minesweeper`, `issue-175-matrix`.
