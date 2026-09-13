---
name: ml-pipelines
description: Observe-mode GitHub ML pipelines for termux-monorepo. Triggers on ML Pipelines, MoneyBall, Issue #213, Issue #175, commit analysis, leaderboard, provider attribution, or extract ledger.
---

# Skill: ml-pipelines

Use `ml_pipelines` for local, stdlib-only scoring of PRs, issues,
commits, and Actions. Never promote a score into a merge, secret,
or issue-to-shell action.

Stages: `issue_175_matrix`, `pr_minesweeper`, `commit_analysis`,
`actions_health`, `provider_attribution`, `lane_consolidation`,
`moneyball_export`, `extract_ledger`, `gitmodules_audit`,
`manus_harvester`.

Run:

```bash
python3 scripts/ml/validate_matrix.py
python3 scripts/ml/run_pipelines.py
python3 -m unittest discover -s tests/ml_pipelines -p 'test_*.py'
```

Complements: `evidence-led-monorepo-ops`, `review-loop`,
`pr-minesweeper`, `issue-175-matrix`, `manus-harvester`.
