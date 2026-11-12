---
id: doe-agentic-logistics-control-plane
title: "DoE agentic ecosystem, PDDL logistics planning and free-inference control plane"
author: ChatGPT
posted_at: 2026-11-11
source: source.md
status: in_review
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: requested
related_issues: [5045, 5136, 5146, 5160, 5176, 5183, 5189, 4979, 5151, 5178]
related_prs: [5045, 5145]
related_branches:
  - proposal/doe-agentic-logistics-control-plane-20261111
related_proposals:
  - provider-family-doe-observatory
gates_required: [proposal-lifecycle, repo-gate, termux-smoke]
---

# MANIFEST — doe-agentic-logistics-control-plane

## Summary

Establish one evidence-governed DoE program that composes the already-forked LangChain ecosystem, the concurrent LangGraph implementation, symbolic logistics planning (PDDL), constraint optimization, and control-systems methods for no-cost inference endpoints. It reuses the repository's existing QUE/QDesk, DoE, ATES, provider/quota, identity, and observability authorities. The initial deliverable is a registered RFP, source map, architecture, offline planning/control experiment plan, and a single queued task—not a production router or a claim that the upstream ecosystem is already operational.

## Authorization boundary

The owner's 2026-11-11 request authorizes RECON, proposal registration, RFP preparation, and the bounded QUE task filing. Implementation beyond this proposal is gated by item-scoped review/acceptance, existing dependency completion, independent verification, and repository gates. This manifest does not authorize new credentials, paid spend, live inference, provider admission, participant issuance, workflow mutation, deployment, production routing, or merge.

## Existing owners to preserve

- LangGraph integration: PR #5045 and its existing branch/skill. Resolve its current-head repo-gate failure before treating it as promoted.
- QDesk/Delphi pipeline: PR #5145 and RFP issue #5146. Reuse its existing Oracle, Delphi gate, feed and acceptance contract.
- Free-inference provider population/cadence: issue #5160; its current prerequisite is PR #5134.
- Participant identity and DoE role-clones: #5136 and #5183, with #5176 and #4979 sequencing preserved.
- Scientific/control specialist role definitions: #5189. This proposal maps the control-systems role into that registry; it does not create another one.
- Provider-family and DoE settings observability: provider-family-doe-observatory / PFDO-005. Extend by citation, not by duplicating its projections.

## Review checklist

- [x] RECON completed against master and named upstream forks
- [x] Existing owners, blocked dependencies and no-duplicate boundaries recorded
- [x] Items DPLC-001 through DPLC-008 itemized
- [ ] Independent reviewer disposition recorded
- [ ] Proposal accepted before implementation items are promoted
- [ ] Proposal/RFP content hash and source manifest bound to QDesk/Delphi review
- [ ] Offline planning/control fixtures and tests validated
- [ ] Live provider work separately admitted by #5160 and the canonical no-cost gate
- [ ] Dual repository gates green on the same PR head
- [ ] Promotion performed only under repository policy

## Links

- RFP: ./RFP.md
- Architecture: ./ARCHITECTURE.md
- Source map: ./SOURCE-MAP.md
- Full README taxonomy: ./ECOSYSTEM-CATALOG.md
- Dispatch observation: ./DISPATCH-OBSERVATION.md
- Items: ./ITEMS.md
- Owner direction and provenance: ./source.md
