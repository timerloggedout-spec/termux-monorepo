---
name: ml-pipeline-ops
description: Keep-alive ML pipeline DAG for termux-monorepo. Load on Issue #175 ML lanes. Never wholesale-merge mega ML PRs.
---

# Skill: ml-pipeline-ops

Session 2026-10-07 04:20 UTC. Product SHA `d0497827` (#1160). Observer tip `a3ee458d` is non-promote.
Keep-alive is `ml/pipelines/` v0.7.0 (command-center). Mega ML PRs stay EXTRACT.

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

## Cycle

RECON → IMPLEMENT → WAIT → VALIDATE → REPEAT

WAIT is concurrent work, not idle parking.

Operator ACTIVE. Agent-Identity: Grok (Administrator)
