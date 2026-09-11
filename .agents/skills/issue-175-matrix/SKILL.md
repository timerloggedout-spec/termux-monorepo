---
name: issue-175-matrix
description: OPERATOR priority matrix for timerloggedout-spec/termux-monorepo Issue #175. Triggers on priority matrix, master functional gate, or operator continue.
---

# Skill: issue-175-matrix

Hard rules: no force-push to master; small green rebased PRs;
repo-gate + termux-smoke; reject Class 3/4; GitLab non-blocking.

Catalog: `docs/ops/ISSUE-175-MATRIX.yaml`.
Validate: `python3 scripts/ml/validate_matrix.py`.
