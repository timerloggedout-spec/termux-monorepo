# ML keep-alive extract (AR-23 / MLP-KEEP-001)

Live master at extract time: `e82a9b16`.

## Why this slice
Wholesale ML PRs `#432 #549 #601 #682 #746 #787 #817` stay EXTRACT/WAIT. This package is the smallest observe-mode DAG that can land without pulling those trees.

## Contract
- Package: `ml/pipelines/`
- Mode: `observe` only
- Dependencies: Python stdlib
- Tests: `ml/pipelines/test_keepalive_dag.py`
- No credentials, no remote inference, no GitHub write from the DAG

## Promote rule
Dual-gate on **this** head SHA. Vercel/Copilot/CodeRabbit are non-gate.
