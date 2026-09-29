# ml/pipelines keep-alive

Slim extract of the ML keep-alive DAG. Issue #175 forbids wholesale merge of
#432 / #549 / #601 / #682 / #746 / #787 / #817.

Re-extracted onto live master `a3423d97` after #836 (lane vocab v2).

Lane vocabulary: `EXTRACT | CANDIDATE | NEED_EVIDENCE | SUPERSEDE`.
HOLD / WAIT / OBSERVE are invalid parking.

```text
python3 -m ml.pipelines.cli status
python3 -m ml.pipelines.cli lanes
python3 -m ml.pipelines.cli run
python3 -m ml.pipelines.cli cctv
python3 -m ml.pipelines.cli matrix
python3 -m unittest discover -s ml/pipelines -p 'test_*.py'
```

Operator ACTIVE. Dual-gate remains promote authority. Vercel non-gate (#772).
Do not restamp LANE-MATRIX policy.
