---
name: issue-175-matrix
description: OPERATOR priority matrix for timerloggedout-spec/termux-monorepo Issue #175. Triggers on priority matrix, master functional gate, or operator continue.
---

# Skill: issue-175-matrix

Hard rules: no force-push to master; small green rebased PRs;
repo-gate + termux-smoke; reject Class 3/4; GitLab non-blocking.

Catalog: `docs/ops/ISSUE-175-MATRIX.yaml`.
Validate: `python3 scripts/ml/validate_matrix.py`.

Live 2026-09-13 next actions:
1. Land observe-mode ML pipelines (this package) — do not merge dirty #432 wholesale
2. Extract #263 only (#264 already closed)
3. Harvester scaffold for #503 — vendors already live
