---
name: ml-pipeline-ops
description: Keep-alive ML pipeline DAG for termux-monorepo. Load on Issue #175 ML lanes. Never wholesale-merge mega ML PRs.
---

# Skill: ml-pipeline-ops

## Hard rules

1. Extract-only for mega ML PRs. Slim tree is `ml/pipelines/`.
2. Dual gates before promote: hygiene+portability + agentic termux smoke.
3. No secrets, no Class 3/4 artifacts, no GPU runners.
4. GitLab / Vercel hobby rate-limit are **non-gate**.
5. Dirty + files>40 + minesweeper overlap → HOLD or EXTRACT.

## Commands

```text
python3 -m ml.pipelines.cli status
python3 -m ml.pipelines.cli lanes
python3 -m ml.pipelines.cli run
python3 -m unittest discover -s ml/pipelines -p 'test_*.py'
```

## Cycle

RECON → INGEST → FEATURES → TRAIN → EVALUATE → (WAIT|HOLD|EXTRACT|PROMOTE) → MONITOR
