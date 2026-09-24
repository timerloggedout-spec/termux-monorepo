# ml/pipelines keep-alive

Slim extract of the ML keep-alive DAG. Issue #175 forbids wholesale merge of #432 / #549 / #601 / #682.

Re-extracted onto live master `03ffb33b` after #787 waited on `ba5f6b6d`.

```text
python3 -m ml.pipelines.cli status
python3 -m ml.pipelines.cli lanes
python3 -m ml.pipelines.cli run
python3 -m ml.pipelines.cli cctv
python3 -m unittest discover -s ml/pipelines -p 'test_*.py'
```

Operator ACTIVE. Dual-gate remains promote authority. Vercel non-gate.
Do not restamp LANE-MATRIX policy.
