---
id: continuous-capability-evolution-lab
title: "Continuous Capability Evolution Laboratory — event-driven FOSS discovery, DoE comparison, and benefit compounding"
author: ChatGPT
posted_at: 2026-11-11
source: "Operator directives: continuous capability discovery and DoE comparison; 2026-11-16 directive to name MOSAIC, formalize SON micro-dense DO statements, and develop the meta-methodology self-improvement architecture."
status: executing
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
related_issues: []
related_prs:
  - 5191
related_branches:
  - feat/ceel-continuous-capability-evolution-20261111
  - feat/mosaic-meta-methodology-20261116
gates_required: [proposal-lifecycle, repo-gate, termux-smoke]
---

# MANIFEST — continuous-capability-evolution-lab

## Summary

CEEL is the continuous capability-discovery and evolution lane inside existing Integration Intelligence and the DoE family. MOSAIC is its named meta-methodology self-improvement program: methods that design, execute, analyze and promote experiments become versioned participants and are evaluated under independent, preregistered evidence.

CEEL and MOSAIC do not create a second orchestrator, telemetry ledger, experiment registry, scheduler, integration registry or merge authority. The repository event plane, Integration Intelligence registry/event contract, DoE experiment record schema, ATES execution discipline, Delphi Oracle/EGM, SHE/3L0/MoneyBall and dual gates remain authoritative.

## Operator authorization

The 2026-11-16 operator directive authorizes the MOSAIC name, SON proposal, detailed specification, documentation work and a bounded pure-Rust recommendation core. Keep live experiment dispatch, paid inference, external account writes, credential provisioning and production routing outside this implementation. Route independently validated changes through the existing repository-managed FA-ADE and proposal lifecycle; MOSAIC itself supplies recommendations and holds no merge or promotion authority.

## Scope boundaries

- CLAUDE.md remains the collaborator entry and CEEL remains the broad capability-evolution lane.
- docs/proposals/registry.yaml, this manifest and ITEMS.md define proposal status and work.
- docs/integrations/registry.json remains the canonical integration inventory.
- docs/integrations/schemas/integration-event.schema.json remains the normalized integration event envelope.
- docs/ops/corpus/EXPERIMENT.schema.json remains the canonical experiment observation contract; MOSAIC adds no competing run receipt.
- docs/ops/DOE-FAMILY.md remains the family structure record; MVT and ATES remain nested under existing doctrine.
- Existing criteria-loop (#1959) and Delphi method-self-application (#1963) are predecessor mechanisms to reconcile, not implementations to duplicate.
- Method versions are immutable; material design changes create a new version/cohort.
- Independent evaluation and existing proposal/dual-gate governance remain mandatory.
- Keep raw prompts, completions, credentials, private traces and restricted customer data out of git.

## Review and promotion

The operator authorized this bounded documentation extension. Independent review and same-SHA repository gates remain required before merge or production promotion. A commit or PR is not a validated method improvement. MOSAIC may recommend a method revision but cannot self-grade or self-promote.

## Checklist

- [x] CEEL foundation merged in PR #5191
- [x] MOSAIC specification and SON notation drafted on feature branch
- [x] Reconcile current #1959 and #1963 issue bodies; both are open/parked, not completed cycles
- [ ] Independent review recorded
- [ ] Proposal lifecycle, repo-gate and Termux smoke pass on the same immutable PR head
- [ ] Method identity and campaign DESIGN integration validated against current schema and code
- [ ] Pilot preregistered and separately admitted before execution
- [ ] Evidence, limitations and deferred runtime work reconciled
- [ ] Merge/promotion only under repository policy

## Links

- ITEMS.md
- docs/superpowers/specs/2026-11-11-continuous-capability-evolution-lab.md
- docs/superpowers/specs/2026-11-16-mosaic-meta-methodology.md
- docs/superpowers/plans/2026-11-11-continuous-capability-evolution-lab.md
- docs/integrations/capability-opportunity-graph.json
- docs/integrations/PLATFORM-COMPARISON.md
