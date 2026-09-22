# ML Pipelines keep-alive

Issue #175 forbids wholesale merge of #432 / #549 / #601 / #682.
This document maps the slim extract in `ml/pipelines/` re-based onto `d10a7a54`.

- DAG: `ml/pipelines/cli.py` + `ml/pipelines/stages/`
- Ranking: `ml/pipelines/moneyball/scorer.py`
- Lane short-circuit: `ml/pipelines/lanes/`
- Gate: `ml/pipelines/contracts/gate.py`
- Replay adapters: `ml/pipelines/replay/` (lineage from #741/#742 — isolated, no runtime import of those packages)
- ICM-CCTV: `ml/pipelines/viz/cctv.py` (Stepie 2087 step 10023)
- Session fixture tip: `d10a7a54`

## Commands

```text
python3 -m ml.pipelines.cli status
python3 -m ml.pipelines.cli lanes
python3 -m ml.pipelines.cli run
python3 -m ml.pipelines.cli cctv
python3 -m ml.pipelines.cli explain 48
python3 -m ml.pipelines.cli gate 707
python3 -m unittest discover -s ml/pipelines -p 'test_*.py'
```

Promote path remains **dual-gate only**. Vercel / GitLab / Copilot / CodeRabbit / Qodo / Devin are non-gate.
