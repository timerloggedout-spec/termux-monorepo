---
name: ml-pipeline-ops
description: Keep-alive ML pipeline DAG for termux-monorepo. Load on Issue #175 ML lanes. Never wholesale-merge mega ML PRs.
---

# Skill: ml-pipeline-ops

Session 2026-09-22 12:18 PDT. Live master `d10a7a54`. Keep-alive child rebases here; #724 SUPERSEDE.

## Hard rules

1. Extract-only for mega ML PRs. Slim tree is `ml/pipelines/`.
2. Dual gates before promote: hygiene+portability + agentic termux smoke.
3. No secrets, no Class 3/4 artifacts, no GPU runners.
4. GitLab / Vercel hobby rate-limit are **non-gate**.
5. Dirty + files>40 + minesweeper overlap → HOLD or EXTRACT.
6. `master_staging_base` (#48) and `stacked_feature_base` (#69) never retarget to master.

## Commands

```text
python3 -m ml.pipelines.cli status
python3 -m ml.pipelines.cli lanes
python3 -m ml.pipelines.cli run
python3 -m ml.pipelines.cli cctv
python3 -m unittest discover -s ml/pipelines -p 'test_*.py'
```

## Cycle

RECON → INGEST → FEATURES → TRAIN → EVALUATE → (WAIT|HOLD|EXTRACT|PROMOTE) → MONITOR

Operator ACTIVE. Agent-Identity: Grok (Administrator)
