---
id: observatory-capability-intake
title: "Observatory → CEEL opportunity intake and refTemplates promotion gates"
author: ChatGPT
posted_at: 2026-11-16
source: source.md
status: posted
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: requested
related_prs: []
related_branches:
  - proposal/observatory-capability-intake-20261116
gates_required: [proposal-lifecycle, repo-gate, termux-smoke]
---

# MANIFEST — observatory-capability-intake

## Summary

Connect the existing Repository Observatory and research-seed intake to CEEL's capability opportunity graph, then govern how validated discoveries become refTemplates references or refTemplates/smods custom-fork gitlinks. This is a focused integration package: Observatory remains the sensing surface, CEEL remains the capability-discovery/evaluation authority, the research-seed format remains the intake handoff, and the existing refTemplates integrity/dual-gate rules remain the promotion boundary.

The proposal does not create another collector, scheduler, event bus, capability graph, integration registry, experiment ledger, or merge authority. It makes the existing documented evolution path operational and testable.

## Scope boundaries

- Repository Observatory remains the source for owned/starred/watching/fork metadata and deterministic candidate signals.
- Research issue templates and scripts/research/research_intake.py remain the existing service/provider seed intake path.
- CEEL owns capability normalization, internal-consumer mapping, candidate comparison, evidence lifecycle and disposition.
- Context Relationship Graph supplies verified repository/file/issue/PR relationships; candidate edges remain explicitly inferred.
- refTemplates/00_Index/SOURCE-MAP.md remains the source navigator.
- refTemplates/15_Research_Repo_Templates/ is metadata-first reference/template material; it does not imply execution or adoption.
- refTemplates/smods/ is reserved for a user-owned/custom-adapted fork with an immutable reviewed pin, shallow gitlink, compatibility evidence and passing gates.
- Existing .gitmodules, refTemplates inventory, submodule integrity and dual-gate workflows remain authoritative.
- No external source code is executed during discovery. No automatic fork, clone, package installation, gitlink creation, upstream sync, secret provisioning, production routing change, merge or deployment is authorized by this proposal.

## Candidate status

The operator-supplied candidate URL, https://github.com/timerloggedout-spec/Time_forkinto, could not be retrieved through the connected GitHub integration (404); repository search did not return a matching accessible repository. This is UNRESOLVED, not proof that the repository does not exist. It may be private, inaccessible to the current integration, renamed, or mistyped. No project identity, license, implementation, activity or capability claim is made. Its evaluation is blocked until the canonical accessible source is established.

## Review and promotion

A candidate can move from discovery to a reference slot only with source provenance, capability evidence, a real internal consumer, license/security/maintenance review and an explicit disposition. A candidate can move into smods/ only when a custom fork is justified, the exact fork/upstream relationship and immutable commit are recorded, required source metadata is present, the gitlink is shallow, and compatibility/security checks pass. Discovery scores are advisory; dual gates and the proposal lifecycle retain promotion authority.

## Checklist

- [x] Existing Observatory, research-seed, CEEL and refTemplates surfaces inspected
- [x] Target repository access limitation recorded without inventing facts
- [ ] Operator confirms/corrects the Time_forkinto canonical source
- [ ] Work items accepted and independently reviewed
- [ ] Implementation and deterministic fixtures completed
- [ ] Proposal lifecycle, repo-gate and Termux smoke pass on the same PR head
- [ ] Promotion disposition and evidence recorded

## Links

- ITEMS.md
- source.md
- CEEL: docs/superpowers/specs/2026-11-11-continuous-capability-evolution-lab.md
- Observatory: docs/repositories/README.md
- Research triggers: docs/ops/RESEARCH-TRIGGERS.md
- refTemplates: docs/ops/REFTEMPLATES-CONSOLIDATION.md
