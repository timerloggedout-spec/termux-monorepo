---
id: integration-intelligence-superpowers
title: "Integration Intelligence foundation and Superpowers engineering methodology"
author: ChatGPT
posted_at: 2026-11-02
source: "Operator directive: make Superpowers available and documented; execute the Integration Intelligence plan"
status: accepted
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
related_prs:
  - 5436
related_branches:
  - feat/integration-intelligence-superpowers
  - feat/unified-feed-adapter-20261114
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — integration-intelligence-superpowers

## Summary

Establish a repository-native Integration Intelligence foundation and make the Superpowers engineering methodology discoverable and usable by repository collaborators. The foundation defines a canonical integration registry, evidence/event contract, adapter boundaries, capability truth labels, and a phased adoption plan for Superpowers, API Impact Mapper, Domino Data Lab, EmpirioLabs AI, tldraw, Cache Stats, Alloy, and Klaviyo.

The foundation now includes canonical event/measurement/batch contracts, append-only ingestion tables in the existing Neon project, and a bounded batch writer with focused offline test coverage authored. Source-specific provider adapters, live Neon migration, historical backfill and multi-surface runtime wiring remain separately gated work.

## Operator amendment — 2026-11-14

The operator explicitly directed consolidation of the repository's many dashboard feeds around one adapter and database contract, with high-throughput ingestion discipline and multiple presentation lanes. This amendment adds IIS-002 through IIS-005. The first implementation slice is restricted to the existing Neon `lane-events` project and operator-provisioned least-privilege roles; it does not create a second database, scheduler, source registry, or merge authority. Existing source ledgers remain authoritative and feed surfaces remain projections.

## Boundaries

- Repository policy in `CLAUDE.md`, proposal lifecycle, dual gates, and human-only permission edges remain authoritative.
- The repository-local Superpowers skill is an integration/bootstrap skill; the upstream Superpowers project remains the canonical source for its full skill library and implementation.
- External systems are evidence and execution providers, never canonical authorities for repository state.
- No secrets, raw prompts, completions, private session transcripts, or sensitive provider payloads are stored in the registry or event ledger.
- No automatic marketing enrollment, provider spend, external project mutation, model deployment, or device/robot command is authorized by this proposal.
- Capability discovery, provider connection, repository adapter implementation, and production promotion are distinct states.

## Review log

### 2026-11-02 — timerloggedout-spec

- Disposition: accepted
- Notes: Operator directive "Do your plan" authorizes the scoped foundation and phased implementation plan.

### 2026-11-14 — timerloggedout-spec

- Disposition: accepted (amendment)
- Notes: Operator directive authorizes IIS-002 through IIS-005. IIS-002 is the current bounded implementation slice; IIS-003–IIS-005 remain queued until their own source mapping and validation evidence are available.

## Checklist

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [x] Operator authorization recorded
- [ ] PR cites `Implements: IIS-001`
- [x] IIS-002 PR #5436 cites `Implements: IIS-002` and links `docs/superpowers/plans/2026-11-14-unified-feed-ingestion.md`
- [ ] repo-gate and termux-smoke green on the same head for IIS-001
- [ ] IIS-002 focused tests and dual gates green on one immutable head
- [ ] Non-author review and current check disposition recorded
- [ ] Close and move to `closed/` only when all gates are terminal

## Links

- ITEMS: ./ITEMS.md
- Design: ../../../superpowers/specs/2026-11-02-integration-intelligence-design.md
- Plan: ../../../superpowers/plans/2026-11-02-integration-intelligence.md
- Unified feed plan: ../../../superpowers/plans/2026-11-14-unified-feed-ingestion.md
