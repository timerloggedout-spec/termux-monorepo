---
name: ml-pipeline-ops
description: Keep-alive ML pipeline DAG for termux-monorepo. Load on Issue #175 ML lanes, moneyball ranking, extract-only #432/#601, dual-gate promote, lineage, providence. Never wholesale-merge mega ML PRs.
---

# Skill: ml-pipeline-ops

## When to load

Issue #175 matrix, labels `ML Pipelines`, PRs #432/#601, ranking PRs, lineage, moneyball.

## Hard rules

1. Extract-only for mega ML PRs. This tree (`ml/pipelines/`) is the keep-alive.
2. Dual gates before promote: `repo_gate.py` + `termux_smoke.py`.
3. No secrets, no Class 3/4 artifacts, no session stores.
4. GitLab / Vercel hobby rate-limit are **non-gate**.
5. Dirty + files>40 + minesweeper overlap → HOLD or EXTRACT, never merge.

## Commands

```text
python3 -m ml.pipelines.cli status
python3 -m ml.pipelines.cli lanes
python3 -m ml.pipelines.cli run
python3 -m unittest discover -s ml/pipelines -p 'test_*.py'
```

## Cycle

RECON → INGEST → FEATURES → TRAIN → EVALUATE → (WAIT|HOLD|EXTRACT|PROMOTE) → MONITOR

Canonical inventory addendum: `docs/ops/SKILLS-INVENTORY-ML.md`.
