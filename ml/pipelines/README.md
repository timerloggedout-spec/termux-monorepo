# ml/pipelines — observe-mode keep-alive (v0.6.0)

Stdlib only. No network. No secrets. No GPU.

```text
python3 -m ml.pipelines.cli status
python3 -m ml.pipelines.cli run
python3 -m ml.pipelines.cli lanes
python3 -m ml.pipelines.cli cctv
python3 -m ml.pipelines.cli matrix
python3 -m ml.pipelines.cli center
python3 -m ml.pipelines.cli bind
python3 -m ml.pipelines.cli drift
python3 -m ml.pipelines.cli extract-plan
python3 -m unittest discover -s ml/pipelines -p 'test_*.py'
```

Lane vocab v2: EXTRACT | CANDIDATE | NEED_EVIDENCE | SUPERSEDE.
HOLD / WAIT / OBSERVE are invalid parking.

Do not wholesale-merge #432 / #549 / #601 / #682 / #746 / #787 / #817.
Do not restamp `docs/ops/LANE-MATRIX.md`.
Do not pulse-comment Issue #175.
