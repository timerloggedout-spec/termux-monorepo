# ml/pipelines keep-alive

Slim extract of the ML keep-alive DAG. Issue #175 forbids wholesale merge of #432 / #549 / #601 / #682.

Re-extracted onto live master `ba5f6b6d` after #746 waited on `d10a7a54`.

```text
python3 -m ml.pipelines.cli status
python3 -m ml.pipelines.cli lanes
python3 -m ml.pipelines.cli run
python3 -m ml.pipelines.cli cctv
python3 -m unittest discover -s ml/pipelines -p 'test_*.py'
```

Operator ACTIVE. Dual-gate remains promote authority. Vercel non-gate.
