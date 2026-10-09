---
name: ml-pipeline-ops
description: Keep-alive ML pipeline DAG for termux-monorepo. Load on Issue #175 ML lanes. Never wholesale-merge mega ML PRs.
---

# Skill: ml-pipeline-ops

Session 2026-10-09. Product SHA `8d36f149` remains the last recorded dual-gate.
Observer tip `9dc1e437` is a help-wanted refresh and is **not** a promote SHA.
Keep-alive is `ml/pipelines/` v0.7.0 (`recon07` binder + command-center). Mega ML PRs stay EXTRACT.

## Hard rules

1. Extract-only for mega ML PRs. Slim tree is `ml/pipelines/`.
2. Dual gates before promote: hygiene+portability + agentic termux smoke. Bind named jobs on **this** SHA.
3. No secrets, no Class 3/4 artifacts, no GPU runners.
4. GitLab / Vercel hobby rate-limit are **non-gate** (#772).
5. Dirty + files>40 + minesweeper overlap → EXTRACT, never wholesale.
6. `master_staging_base` (#48, #788) never retarget to master.
7. Do **not** restamp `docs/ops/LANE-MATRIX.md` (policy SSOT). Live board is generated.
8. Do **not** pulse-comment Issue #175. Edit the issue body only when intent changes.
9. Lane vocab v2: EXTRACT | CANDIDATE | NEED_EVIDENCE | SUPERSEDE. HOLD/WAIT/OBSERVE are invalid parking.
10. Observer help-wanted refreshes are not promote SHAs.

## Commands

```text
python3 -m ml.pipelines.cli status
python3 -m ml.pipelines.cli lanes
python3 -m ml.pipelines.cli run
python3 -m ml.pipelines.cli cctv
python3 -m ml.pipelines.cli matrix
python3 -m ml.pipelines.cli center
python3 -m ml.pipelines.cli bind
python3 -m ml.pipelines.cli drift
python3 -m ml.pipelines.cli extract-plan
python3 -m ml.pipelines.cli recon
python3 -m ml.pipelines.cli steward
python3 -m ml.pipelines.cli explain 682
python3 -m ml.pipelines.cli gate 48
python3 -m unittest discover -s ml/pipelines -p 'test_*.py'
```

## Cycle

RECON → IMPLEMENT → WAIT → VALIDATE → REPEAT

WAIT is concurrent work, not idle parking.

Operator ACTIVE. Agent-Identity: Grok (Administrator)
