# ML Pipelines keep-alive

Issue #175 forbids wholesale merge of #432 / #549 / #601 / #682.
This document maps the slim extract in `ml/pipelines/`.

- DAG: `ml/pipelines/cli.py`
- Ranking: `ml/pipelines/moneyball/scorer.py`
- Gate: `ml/pipelines/contracts/gate.py`

Promote path remains **dual-gate only**.
