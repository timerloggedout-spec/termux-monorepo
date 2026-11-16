# ML Pipelines keep-alive

Issue #175 forbids wholesale merge of #432 / #549 / #601 / #682.
v0.8.0 adds `ml/pipelines/recon08/`: an observe-only binder on live master.
The v0.6.0 command-center DAG stays. Product SHA remains `8d36f149`.
Observer tip `677a2d72` (sweep receipt) is not a promote.

- DAG: `ml/pipelines/cli.py` + `ml/pipelines/stages/`
- Ranking: `ml/pipelines/moneyball/scorer.py`
- Lane short-circuit: `ml/pipelines/lanes/` (vocab v2 after #836)
- Recon binder: `python3 -m ml.pipelines.cli recon` and `steward`
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
python3 -m ml.pipelines.cli recon
python3 -m ml.pipelines.cli steward
python3 -m ml.pipelines.cli explain 48
python3 -m ml.pipelines.cli gate 682
python3 -m unittest discover -s ml/pipelines -p 'test_*.py'
```

Promote path remains **dual-gate only**. Vercel / GitLab / Copilot / CodeRabbit / Qodo / Devin are non-gate.
Do not restamp `docs/ops/LANE-MATRIX.md`.
Do not treat sweep or help-wanted observer commits as product promotes.
Do not promote stale recon07 PR #1188.
