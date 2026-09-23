# ML Pipelines (keep-alive extract)

Implements: `MLP-KEEP-001`

This tree is the **extract-only** keep-alive for Issue #175 ML lanes
(`#432` / `#601` remain NO-GO wholesale). It is a runnable DAG, not a
notebook dump.

## Dual gate before any promote

```text
python3 scripts/ci/repo_gate.py
python3 scripts/ci/termux_smoke.py
python3 -m ml.pipelines.cli status
python3 -m unittest discover -s ml/pipelines -p 'test_*.py'
```

## Stages

| id | name | purpose |
|----|------|---------|
| 00 | RECON | evidence snapshot |
| 10 | INGEST | event normalize |
| 20 | FEATURES | lag / mergeability / drift |
| 30 | TRAIN | moneyball weights |
| 40 | EVALUATE | lane classification |
| 50 | DEPLOY | promote packet (gated) |
| 60 | MONITOR | WAIT → VALIDATE |

Agent-Identity: Grok (Administrator)
