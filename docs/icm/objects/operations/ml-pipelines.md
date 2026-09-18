---
type: object
cluster: operations
universe: live
status: verified
entity: ml_pipelines/
verified_at: 2026-09-16
---

# ML Pipelines

Observe-mode GitHub ML pipelines live in `ml_pipelines/`.

Run `python3 scripts/ml/run_pipelines.py`. Gates remain
`scripts/ci/repo_gate.py` and `scripts/ci/termux_smoke.py`.

MoneyBall scores are decision-support. Dispositions from
`pr-minesweeper` do not merge. Issue #175 matrix YAML is
fail-closed via `scripts/ml/validate_matrix.py`.

## Connected to

- **owns:** observe-mode DAG, Issue #175 matrix bind, PR minesweeper.
- **owned-by:** proposal `ml-pipelines-init`.
- **joins:** Actions health, provider attribution, reviewer-noise taxonomy.
