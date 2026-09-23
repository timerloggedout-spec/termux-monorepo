---
name: ml-pipeline-ops
description: CI twin of .agents/skills/ml-pipeline-ops. Production reconciliation for the keep-alive DAG.
---

# CI skill: ml-pipeline-ops

Run `python3 -m unittest discover -s ml/pipelines -p 'test_*.py'` as a non-blocking job until the dual-gate workflow explicitly lists it.

Do not add GPU runners. Do not download models. Do not write secrets to artifacts.
