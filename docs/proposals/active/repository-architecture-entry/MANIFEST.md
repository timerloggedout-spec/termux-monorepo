# Repository Architecture Entry — Proposal Manifest

**ID:** repository-architecture-entry  
**Status:** executing  
**Priority:** P1  
**Owner:** ChatGPT — documentation implementation  
**Operator authorization:** accepted for the bounded documentation change  
**Canonical output:** repository root `architecture.md`  
**Implementation branch:** `docs/architecture-versioning-automation-20261122`

## Objective

Establish one repository-wide architecture entry that routes collaborators to canonical domain sources, summarizes major system planes, maps repository data flows, and provides a navigable directory taxonomy.

## Scope

- Root architecture entry with ToC and nested taxonomy.
- Mermaid data-flow source under `docs/ops/diagrams/`.
- Entry-point links in root `CLAUDE.md`, root `README.md`, `docs/icm/CLAUDE.md`, and `docs/architecture/README.md`.
- Proposal registry and work-item record.
- Semantic architecture versioning, deterministic source/render manifest, and automated architecture diagram refresh through the existing workflow.

## Authority and boundaries

- Domain contracts and implementation sources retain semantic ownership.
- The architecture entry remains a navigation and synthesis layer.
- Solid and dashed Mermaid edges distinguish implemented/documented paths from optional, intended, contract-only, or partially verified joins.
- The directory taxonomy remains intentionally selective; dynamic inventories require live-tree revalidation.

## Acceptance

- [x] Root `architecture.md` includes ToC, system taxonomy, directory taxonomy, data-flow entities/origins/producers/transformations/stores/consumers, canonical links, and change-impact routing.
- [x] Mermaid source renders successfully.
- [x] 36 internal architecture links resolve against the branch tree.
- [x] Root collaborator, README, ICM, and architecture-index entry points link to the root architecture entry.
- [ ] Proposal registry validator passes with the manifest and work items present.
- [ ] Repository gate and Termux smoke pass on the same head.
- [ ] Required PR checks complete and the merged master head is re-fetched.
- [x] Initial SemVer baseline, versioning contract, changelog, and architecture-governance map added.
- [x] Deterministic manifest generator and ten focused tests pass in the local fixture suite.
- [ ] Existing workflow renders architecture flow SVGs, validates the manifest, uploads PR evidence, and refreshes trusted master projections.

## Evidence

- PR: https://github.com/timerloggedout-spec/termux-monorepo/pull/5744
- Initial implementation commit: `7719a5ff49b17ec902b613d383db70a1e0d617a4`
- Mermaid render: successful in ChatGPT Mermaid preview.
- Link audit: 36 checked, 0 missing.
- CI discovered a missing proposal manifest; this follow-up supplies the required file before the next validation cycle.

## Review log

| Date | Actor | Event | Evidence / disposition |
|---|---|---|---|
| 2026-11-21 | ChatGPT | Initial documentation and data-flow map committed | PR #5744; registry validator exposed missing MANIFEST.md; follow-up adds this manifest. |


## Architecture v2 — linked modules and snapshot audit

- Flow index: docs/architecture/flows/README.md
- Seven detailed Markdown maps and seven paired Mermaid sources are linked from root architecture.md.
- Mermaid.ai project: https://mermaid.ai/app/projects/affbc609-b2b7-420c-af5b-ca0ccb74fe14
- Existing root diagram document ID updated in place: 080c5454-1215-40a8-afb5-7ef30e42dfcb
- Focused Mermaid.ai saves reached the account diagram limit; all six editable sources are committed in the repository.
- archwiz/DATA_FLOW_MANIFEST.md is a zero-byte tracked blob at observed master SHA 5135731c389c6b1b8ed8332b3415a60f8163c2a1. Generator writes to $HOME/archwiz/DATA_FLOW_MANIFEST.md and omits source SHA / tree SHA / input digest.
- Actual local generated_at: unknown; it is not inferred from audit date.


## Current implementation PR

- PR #5770: https://github.com/timerloggedout-spec/termux-monorepo/pull/5770
- Branch: docs/architecture-versioning-automation-20261122
- Current status: open draft; exact-head validation and independent review pending.

## Architecture versioning extension — REPO-ARCH-007

- Design: docs/superpowers/specs/2026-11-22-architecture-versioning-design.md
- Implementation plan: docs/superpowers/plans/2026-11-22-architecture-versioning-plan.md
- Version contract: docs/architecture/VERSIONING.md
- Initial version: 1.0.0
- Manifest generator: scripts/ci/architecture_docs.py
- Architecture flow: docs/architecture/flows/architecture-governance.md and architecture-governance.mmd
- Focused test-first sequence: missing generator produced the expected initial failure; implementation then passed 10 focused tests locally.
- PR validation, trusted master refresh, and final master re-fetch remain pending runtime evidence.
