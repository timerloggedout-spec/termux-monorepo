---
id: cost-of-remembering-integration
title: "RinDig cost-of-remembering_fork ICM evidence lane"
author: timerloggedout-spec
posted_at: 2026-09-10
source: operator-directive
status: executing
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
related_prs: []
related_branches:
  - feat/rindig-cost-of-remembering-icm
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — Cost of Remembering Integration

## Summary

Owns and pins `timerloggedout-spec/cost-of-remembering_fork` (fork of RinDig/cost-of-remembering) as a shallow reference submodule under `refTemplates/smods/`. Adds a native ICM knowledge card and updates coverage / integration docs. Content-Agent-Routing-Promptbase remains the layered-routing companion; AuditEngine is staged for a subsequent adapt pass.

## Review log

### 2026-09-10 — Operator directive

- Disposition: accepted for execution.
- Notes: "do EVERYTHING. Build The Future Now." Explicit targets: cost-of-remembering + Content-Agent-Routing-Promptbase; AuditEngine adapt after.

## Checklist

- [x] Fork created: timerloggedout-spec/cost-of-remembering_fork
- [x] Branch: feat/rindig-cost-of-remembering-icm
- [x] Knowledge card: docs/icm/objects/knowledge/cost-of-remembering.md
- [ ] .gitmodules + gitlink (submodule add) — requires local clone or follow-up commit
- [ ] method-coverage + ICM-ARCHITECT-INTEGRATION updates
- [ ] template-candidates.yaml entry
- [ ] PR opened
- [ ] Dual gates green

## Links

- Fork: https://github.com/timerloggedout-spec/cost-of-remembering_fork
- Upstream: https://github.com/RinDig/cost-of-remembering
- Related: Content-Agent-Routing-Promptbase (already pinned), AuditEngine (adapt next)
