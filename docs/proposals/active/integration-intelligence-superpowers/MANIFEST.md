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
related_prs: []
related_branches:
  - feat/integration-intelligence-superpowers
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — integration-intelligence-superpowers

## Summary

Establish a repository-native Integration Intelligence foundation and make the Superpowers engineering methodology discoverable and usable by repository collaborators. The foundation defines a canonical integration registry, evidence/event contract, adapter boundaries, capability truth labels, and a phased adoption plan for Superpowers, API Impact Mapper, Domino Data Lab, EmpirioLabs AI, tldraw, Cache Stats, Alloy, and Klaviyo.

This is a documentation-and-contract foundation. It does not claim that external providers are authenticated, that adapters are implemented, or that any provider is a source of truth.

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

## Checklist

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [x] Operator authorization recorded
- [ ] PR cites `Implements: IIS-001`
- [ ] repo-gate and termux-smoke green on the same head
- [ ] Non-author review and current check disposition recorded
- [ ] Close and move to `closed/` only when all gates are terminal

## Links

- ITEMS: ./ITEMS.md
- Design: ../../../superpowers/specs/2026-11-02-integration-intelligence-design.md
- Plan: ../../../superpowers/plans/2026-11-02-integration-intelligence.md
