---
id: rindig-eduba-consolidation
title: "RinDig ICM + EDUBA repository consolidation"
author: timerloggedout-spec
posted_at: 2026-09-23
source: operator-directive
status: executing
priority: P0
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
related_prs: []
related_branches:
  - feat/rindig-eduba-consolidation
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — RinDig / ICM / EDUBA Consolidation

Consolidate RinDig repositories already used by termux-monorepo, reconcile owned fork drift, register EDUBA and psychometric evaluation sources, and add reproducible GitHub Actions inventory for branches, commits, and workflows.

Hard boundary: upstream repositories remain authoritative for upstream history; owned forks are customization boundaries; Devin and DeepWiki are discovery-only; no secrets or private wiki content are imported.
