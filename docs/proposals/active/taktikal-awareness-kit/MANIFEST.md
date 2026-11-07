---
id: taktikal-awareness-kit
title: "T.A.K. — Taktikal Awareness Kit: COP, OODA, and actor-network emergence"
author: ChatGPT
posted_at: 2026-11-05
source: "Registered T.A.K. lens doctrine, repository evidence, and cited public military/COP research"
status: posted
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: requested
  - id: ChatGPT
    role: author+executor
    status: executing
related_issues: [4496]
related_prs: []
related_branches:
  - docs/taktikal-awareness-ooda-architecture
gates_required:
  - proposal-lifecycle
  - repo-gate
  - termux-smoke
---

# MANIFEST — Taktikal Awareness Kit

## Summary

Turn the already-registered T.A.K. lens into a concrete, evidence-backed awareness architecture. T.A.K. composes repository, agent-fleet, workflow, and approved procurement/registration observations into a time-aware common picture. It adapts the useful patterns of COP, OODA feedback, multi-actor orientation, and decentralized execution while preserving provenance, uncertainty, source freshness, and human decision authority.

## System boundaries

- RIDP owns reusable evidence acquisition, caching, freshness, and context envelopes.
- Context Relationship Graph owns repository relationship extraction and evidence-linked navigation.
- T.A.K. owns the awareness lens, entity tracks, emergence signals, and role-specific picture projections.
- Existing GitHub Agentic Collaboration owns claims, dependencies, routing, execution, review, and integration.
- Existing SHE, ATES, dispatch-tree, tracking, and telemetry surfaces remain their owners' systems; candidate bindings are not promoted by this proposal.

T.A.K. is not a new orchestrator, task ledger, permission system, collector fleet, or canonical data lake.

## Scope

1. Versioned entity, observation, relationship, and track-event contracts.
2. Explicit epistemic status, provenance, freshness, coverage, and conflict handling.
3. Read-only repository COP using existing evidence surfaces.
4. Procurement/registration actor-network emergence design and integration with repeat-crawl source receipts.
5. OODA decision-support cards routed through existing authorization and control-plane workflows.
6. Evaluation, observability, and efficiency criteria.

## Non-negotiable boundaries

- The registered T.A.K. doctrine and K spelling are preserved.
- New actor-network observations enter unvalenced; competitive SWOT dual-valence is evidence-assigned and dated.
- Observed, inferred, candidate, disputed, stale, and unknown states remain distinct.
- No silent entity merge, overwrite, or source-conflict resolution.
- No external outreach, procurement action, merge, deployment, or other consequential action without existing explicit authority.
- No credentials, cookies, session data, or unnecessary personal data in evidence records.
- Missing telemetry remains unknown, never zero.
- Government TAK is an external reference domain, not this project's product or imported doctrine.

## Dependencies

- `docs/ops/LENS-FRAME.md`
- `docs/ops/LENS-TEMPLATE-TRIGGER.md`
- `docs/ops/DOE-FAMILY.md`
- `docs/ops/AGENT-TEAM-DEVELOPMENT-LANES.md`
- RIDP architecture and source evidence work
- Context Relationship Graph
- Issue #4496 repeat-crawl ingest/store proposal

## Promotion

Promotion requires proposal-lifecycle, repo-gate, and Termux smoke evidence on the same immutable head SHA; source-to-claim traceability; validated epistemic and freshness semantics; and review of all open findings. A green workflow is evidence about that workflow only. This PR establishes the architecture and proposal package; it does not claim runtime collectors, dashboards, or production feed integrations are deployed.
