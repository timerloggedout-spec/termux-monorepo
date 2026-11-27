---
id: polyglot-localization
title: "PolyGlot localization: Urdu-first Teammate Portal and provider DOE"
author: ChatGPT
posted_at: 2026-11-27
source: docs/superpowers/specs/2026-11-27-polyglot-urdu-portal-design.md
status: executing
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
related_prs: [5940]
related_branches:
  - feat/polyglot-urdu-portal-20261127
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — polyglot-localization

## Summary
Establish repository-owned localization infrastructure and deliver Urdu-first Teammate Portal shell support, including locale registry, source mappings, translation manifests, provider registry, pre-registered DOE comparison, and optional consent-based feedback.

## Scope
- localization/: locale registry, catalogs, mappings, manifests, schemas, provider registry, DOE campaign.
- Teammate Portal renderer: English/Urdu output variants, language navigation, RTL metadata and layout.
- Tests and docs: validation, design, implementation plan, and proposal records.

## Authority
Human-reviewed translations are publication-eligible. Provider candidates and DOE results remain advisory until reviewed. Provider secrets and account setup remain external to the repository. Feedback collection requires explicit opt-in.

## Review log
| Date | Actor | Event | Evidence |
|---|---|---|---|
| 2026-11-27 | ChatGPT | Proposal registered for implementation | Branch feat/polyglot-urdu-portal-20261127; PR pending |

## Checklist
- [x] Design and plan recorded
- [x] Work items registered
- [ ] Locale catalogs and schemas validated
- [ ] Portal Urdu/RTL rendering verified
- [ ] DOE run records validated
- [ ] Repository gates pass on candidate SHA
- [ ] Independent review and promotion
