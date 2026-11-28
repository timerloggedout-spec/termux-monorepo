---
id: cell-the-living-machine
title: "CELL: THE LIVING MACHINE — science, engineering and real-world making platform"
author: ChatGPT
posted_at: 2026-11-27
source: source.md
status: draft
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: requested
  - id: ChatGPT
    role: author-executor
    status: executing
related_issues:
  - 5952
related_prs:
  - 5954
related_branches:
  - feature/cell-living-machine-architecture-v2
related_repos:
  - https://github.com/timerloggedout-spec/termux-monorepo
  - https://github.com/Research-Astute/molecular-biology-research
  - https://github.com/search-astute-ly
gates_required:
  - repo-gate
  - termux-smoke
---

# MANIFEST — cell-the-living-machine

## Summary

Establish an original science and engineering creation platform that makes molecular, cellular and industrial systems playable through exploration, simulation, factory automation, engineering design, manufacturing and specialist research. The project uses three coordinated planes: Research Astute for reusable research references; Search Astutely for search execution, aggregation, and result snapshots; and Termux MonoRepo for developer lanes, tools, project profiles, and orchestration. The initial database map spans 26 candidate sources across structures, sequences, interactions, pathways, chemistry, enzyme kinetics, cell context, literature, and education. A dedicated game repository owns the playable product and is registered through the MonoRepo project-profile family.

## Architecture decision

A + B + C operate together with separate ownership:

| Plane | Canonical owner | Responsibility |
|---|---|---|
| A — Game product | Dedicated `cell-the-living-machine` repository | Game source, assets, runtime, builds, tests, release artifacts |
| B — Developer control plane | `timerloggedout-spec/termux-monorepo` | Project profile, game lanes, specialist contexts, tool profiles, CI, QA routing, integration contracts |
| C1 — Reusable research | `Research-Astute/molecular-biology-research` | Reusable molecular/cellular biology research records, source registry, mechanisms, claims, and provenance |
| C2 — Search aggregation | `search-astute-ly` organization | Search jobs, aggregated results, snapshots, source links, research-discovery workflows |
| C3 — Scientific authorities | External scientific databases | Canonical structures, sequences, annotations, pathways, molecules, and literature records |

Cross-plane integration uses stable project IDs, repository IDs, versioned manifests, source accessions, and API contracts. Local symlinks may support a developer workspace view; manifests and versioned interfaces remain the cross-repository contract.

## Existing game-lane fit

The MonoRepo already defines Game Development & Production, Game Player Machines & Genre Teams, Game QA & Accessibility, and Game ML Research. The project attaches to these existing lanes and uses their separate responsibilities. Genre remains an additive facet set rather than a fixed team identity.

## Audience and progression model

Knowledge access is ubiquitous. Every participant can reach the same underlying knowledge graph. Field, Mechanism, Quantitative, Structural, and Research lenses vary explanatory resolution and instrumentation. Challenge profiles tune resource constraints, time pressure, uncertainty, and scenario coupling. Progression follows demonstrated curiosity and mastery signals rather than age.

## Seed surface

The full iJEP Studio channel is the initial visual and topic-discovery surface. The initial upload inventory captures all 125 channel entries across two playlist pages, including video IDs, titles, publication metadata, durations, views, and title-derived topic candidates. Per-video descriptions, transcripts, linked papers, structure IDs, technical comments, and asset rights form the next extraction pass. iJEP Studio's own production descriptions emphasize scientific review and real structural references; media reuse follows the creator's published license terms and any separately granted permissions.

## Current status

- MonoRepo scope profile: drafted under `.config/llm_map/profiles/projects/`; project manifest and registry are in `ops/projects/`; PR #5954 is open for review.
- Dedicated game repository: created as private `timerloggedout-spec/cell-the-living-machine` (repository ID `1475194740`, default branch `main`); planning scaffold committed; public transition is queued through an owner-authorized GitHub Actions workflow.
- Research Astute: owner organization verified; private `molecular-biology-research` repository created (ID `183701786`) with a 26-provider reusable source registry and three initial mechanism dossiers.
- Search Astutely: owner organization verified; current `manus-public-ui-research` repository is scoped to public Manus UI research. Scientific search aggregation endpoint and Enterprise account preservation require review.
- Scientific database catalog: 26 candidate sources mapped across nine research domains; source-specific adapter admission follows API, terms, and provenance review.
- Engineering platform: concept-to-production workflow, shared equipment registry, provider directory and central player profile are specified.
- Visual pipeline: DCC-MCP Blender adapter is the preferred typed-tool candidate; Molecular Nodes and OpenUSD are in the toolchain review.
- Hardware: low-tier Android and browser compatibility is the baseline; high-fidelity studio rendering is a separate tier.
- Academy: AMD ROCm and NVIDIA DLI/OpenUSD/Omniverse pathways are mapped to practical portfolio evidence.
- Engine and renderer: selection pending a bounded prototype comparison.

## Review log

### 2026-11-27 — ChatGPT

- Disposition: draft package created for Operator review.
- Evidence: current MonoRepo game-lane documents, game context schema, research-seed intake, GitHub organization/repository search, ResearchAstute README/resources/license files, and official database API documentation.
- Decision: use A + B + C with separate repositories and manifests; use versioned API contracts across repository boundaries.

## Checklist

- [x] Proposal package and scoped items created.
- [x] Existing game-lane fit recorded.
- [x] Three-plane architecture and project profile drafted.
- [x] Scientific database discovery catalog drafted.
- [x] Knowledge-lens model drafted.
- [ ] Operator review and acceptance recorded.
- [x] Dedicated game repository provisioned.
- [ ] Search Astutely runtime and account ownership verified.
- [ ] Research Astute reuse and licensing scope approved.
- [ ] Engine selection and prototype acceptance contract approved.
- [ ] Source and science review completed for the first playable slice.

## Links

- [ITEMS](./ITEMS.md)
- [DEBATE](./DEBATE.md)
- [Source evidence](./source.md)
- [Audience and challenge opportunity map](./AUDIENCE_AND_OPPORTUNITY_MAP.yaml)
- [Research Astute contract](./RESEARCH_ASTUTE_CONTRACT.yaml)
- [Search aggregation contract](./SEARCH_AGGREGATION_CONTRACT.yaml)
- [Research Astute science repository](https://github.com/Research-Astute/molecular-biology-research)
- [Scope profile pointer](./PROJECT_PROFILE.yaml)
- [Canonical scope profile](../../../../.config/llm_map/profiles/projects/cell-the-living-machine.json)
- [Game project manifest](../../../../ops/projects/manifests/cell-the-living-machine.yaml)
- [Project registry](../../../ops/projects/registry.yaml)
- [Research map](./RESEARCH_MAP.yaml)
- [Database catalog](./DATA_SOURCES.yaml)
- [iJEP Studio 125-item channel inventory](./research/ijep-studio-channel-inventory.json)
- [Content taxonomy](./CONTENT_TAXONOMY.yaml)
- [Game design](./GAME_DESIGN.md)
- [Provenance contract](./PROVENANCE.md)
- [Implementation plan](../../../superpowers/plans/2026-11-27-cell-living-machine-architecture.md)
