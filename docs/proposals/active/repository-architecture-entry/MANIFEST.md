# Repository Architecture Entry — Proposal Manifest

**ID:** repository-architecture-entry  
**Status:** executing  
**Priority:** P1  
**Owner:** ChatGPT — documentation implementation  
**Operator authorization:** accepted for the bounded documentation change  
**Canonical output:** repository root `architecture.md`  
**Implementation branch:** `docs/repository-architecture-entry-20261121-v2`

## Objective

Establish one repository-wide architecture entry that routes collaborators to canonical domain sources, summarizes major system planes, maps repository data flows, and provides a navigable directory taxonomy.

## Scope

- Root architecture entry with ToC and nested taxonomy.
- Mermaid data-flow source under `docs/ops/diagrams/`.
- Entry-point links in root `CLAUDE.md`, root `README.md`, `docs/icm/CLAUDE.md`, and `docs/architecture/README.md`.
- Proposal registry and work-item record.

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
