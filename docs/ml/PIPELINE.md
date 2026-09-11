# GitHub ML Pipelines

Observe-mode pipelines for Issue #213. Stdlib only. No secrets. No
issue/comment-to-shell. History files are protected.

## Stages

| Stage | Item | Output |
|---|---|---|
| `issue_175_matrix` | MLP-02 | Watch-list binding for #175 |
| `pr_minesweeper` | MLP-03 | Disposition per open PR |
| `commit_analysis` | MLP-01 | Prefix/author histogram |
| `actions_health` | MLP-01 | Failure vs skip classification |
| `provider_attribution` | MLP-01 | Bot vs shared-login histogram |
| `lane_consolidation` | MLP-03 | Drift flags |
| `moneyball_export` | MLP-01 | Decision-support leaderboard |

Run:

```bash
python3 scripts/ml/run_pipelines.py --snapshot ml_pipelines/fixtures/ops-snapshot.json
python3 scripts/ml/validate_matrix.py docs/ops/ISSUE-175-MATRIX.yaml
python3 -m unittest discover -s tests/ml_pipelines -p 'test_*.py'
```
