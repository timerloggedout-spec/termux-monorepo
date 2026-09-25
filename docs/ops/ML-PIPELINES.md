# ML Pipelines keep-alive

Issue #175 forbids wholesale merge of #432 / #549 / #601 / #682.
This document maps the slim extract in `ml/pipelines/` re-based onto live master `a3423d97`.

- DAG: `ml/pipelines/cli.py` + `ml/pipelines/stages/`
- Ranking: `ml/pipelines/moneyball/scorer.py`
- Lane short-circuit: `ml/pipelines/lanes/` (vocab v2 after #836)
- Gate: `ml/pipelines/contracts/gate.py`
- Replay adapters: `ml/pipelines/replay/`
- ICM-CCTV: `ml/pipelines/viz/cctv.py` (Stepie 2087 step 10023)
- Latest fixture: `ml/pipelines/fixtures/session_20260925.json`

## Commands

```text
python3 -m ml.pipelines.cli status
python3 -m ml.pipelines.cli lanes
python3 -m ml.pipelines.cli run
python3 -m ml.pipelines.cli cctv
python3 -m ml.pipelines.cli explain 48
python3 -m ml.pipelines.cli gate 682
python3 -m unittest discover -s ml/pipelines -p 'test_*.py'
```

Promote path remains **dual-gate only**. Vercel / GitLab / Copilot / CodeRabbit / Qodo / Devin are non-gate.
Do not restamp `docs/ops/LANE-MATRIX.md`.
