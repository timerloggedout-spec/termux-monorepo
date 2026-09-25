---
name: ml-pipeline-ops
description: Keep-alive ML pipeline DAG for termux-monorepo. Load on Issue #175 ML lanes. Never wholesale-merge mega ML PRs.
---

# Skill: ml-pipeline-ops

Session 2026-09-25 14:10 PDT. Live master `a3423d97` after #836 (lane vocab v2).
Keep-alive child rebases here; #817 / #787 / #746 / #682 SUPERSEDE-or-EXTRACT.

## Hard rules

1. Extract-only for mega ML PRs. Slim tree is `ml/pipelines/`.
2. Dual gates before promote: hygiene+portability + agentic termux smoke. Bind the named jobs, not combined status.
3. No secrets, no Class 3/4 artifacts, no GPU runners.
4. GitLab / Vercel hobby rate-limit are **non-gate** (#772).
5. Dirty + files>40 + minesweeper overlap → EXTRACT, never wholesale.
6. `master_staging_base` (#48, #788) never retarget to master.
7. Do **not** restamp `docs/ops/LANE-MATRIX.md` (policy SSOT). Live board is generated.
8. Do **not** pulse-comment Issue #175. Edit the issue body only when intent changes.
9. Lane vocab v2: EXTRACT | CANDIDATE | NEED_EVIDENCE | SUPERSEDE. HOLD/WAIT/OBSERVE are invalid parking.

## Commands

```text
python3 -m ml.pipelines.cli status
python3 -m ml.pipelines.cli lanes
python3 -m ml.pipelines.cli run
python3 -m ml.pipelines.cli cctv
python3 -m ml.pipelines.cli matrix
python3 -m ml.pipelines.cli explain 682
python3 -m ml.pipelines.cli gate 48
python3 -m unittest discover -s ml/pipelines -p 'test_*.py'
```

## Cycle

RECON → INGEST → FEATURES → TRAIN → EVALUATE → (EXTRACT|CANDIDATE|NEED_EVIDENCE|SUPERSEDE) → MONITOR

Operator ACTIVE. Agent-Identity: Grok (Administrator)
