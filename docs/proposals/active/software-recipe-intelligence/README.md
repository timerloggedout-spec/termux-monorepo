# Software Recipe Intelligence — Research and Architecture Proposal

**Working descriptor:** Software Recipe Intelligence  
**Model abbreviation:** SRM — Software Recipe Model (model only; not the project name)  
**Project identity:** intentionally unassigned pending naming review  
**Architecture owner:** intentionally unassigned pending system-wide ownership recon  
**Status:** research/design candidate; no execution, production, or promotion authority

## Purpose

Develop a reusable, evidence-bearing representation of software capabilities as recipes: versioned descriptions of intent, ingredients, preconditions, ordered procedures, environments, outputs, evaluation contracts, provenance, and evolution.

The scope is deliberately broader than build scripts or file reconstruction. Candidate recipe subjects include algorithms, APIs, libraries, workflows, agent skills, agent teams, integrations, experiments, operational procedures, recovery paths, and compositions of these capabilities.

A recipe is initially **descriptive and advisory**. It does not grant permission to execute its steps. Execution, when eventually considered, must be bound to existing authorization, sandboxing, audit, and promotion authorities.

## Corrections and identity boundaries

- GRIMOIRE already exists. It remains the repository's established lexicon/protocol and naming vocabulary. This project does not appropriate its name, create a second Grimoire, or invent a competing naming authority.
- MOSAIC and MOSAIC Brain already exist. They are relevant architecture participants, not presumed owners.
- The repository has multiple Brain, intelligence, orchestration, graph, memory, experiment, and agent systems. No one of them is selected as owner by this proposal.
- The owner-supplied `META-brain.rs` → `mosaic.brain.rs` rename is one example of lineage-sensitive naming. It is not an instruction to locate this work in MOSAIC Brain.
- Existing Repo Replay and Commit Replay already use recipe concepts for distinct provenance/reconstruction and Git-fragment composition planes. They are prior art and integration boundaries, not blank space to duplicate.
- SRI is a useful descriptive phrase, but **SRI is not adopted as the project acronym** because it collides with SRI International, the research institute associated with Siri's origins. See the name register.

## Architectural principle

**Discover first; assign ownership second.** This proposal will map existing systems, their contracts, authorities, and deployment status before recommending whether the capability should be:
1. an extension to one existing system;
2. a shared domain model consumed by several systems;
3. a set of adapters over existing authorities; or
4. a genuinely distinct component, only if a demonstrated gap remains.

No new Brain, graph database, memory store, experiment ledger, orchestrator, notation system, integration registry, or promotion authority is assumed.

## Existing authorities to reuse

- Repo Replay and Commit Replay for their existing, deliberately separate recipe/pointer/replay models.
- Native Orchestration Contracts: `ORCHESTRATION-TREATMENT.schema.json` for repeatable orchestration patterns and `ORCHESTRATION-RECEIPT.schema.json` for cycle observations.
- The Monorepo Brain's proposed domain-cognition contract as a candidate integration surface only; the broad model is not assigned to a Brain, and MOSAIC Brain's narrower `methodology_intelligence` scope is not presumed to own it.
- Agent Team Control Plane, Termux Multi-Agent, and Temporal AI Cookbook patterns as existing workflow/agent recipe sources; their deployment and adoption states must remain evidence-qualified.
- Context Relationship Graph for metadata-only, evidence-qualified relationships.
- Integration Intelligence registry and event contract for provider/capability identities and normalized integration evidence.
- CEEL for continuous discovery, classification, mapping, comparison, and governed evolution.
- DoE and `docs/ops/corpus/EXPERIMENT.schema.json` for preregistered experiments and run observations.
- Delphi/EGM for independent challenge and admission.
- SHE, 3L0, MoneyBall, ATES, WTCV/TCV/TPV and repository-native evaluation for outcomes, quality, cost, throughput, and evidence.
- ICM and proposal registries for ownership, source routing, lifecycle, and navigation.
- Linguist, Siglary, Grimoire, and the existing Name Forge for terminology and notation governance.
- Existing Brain kernels, planners, Kahn DAG, and orchestration systems only after their actual contracts and boundaries are mapped.

## Initial work sequence

1. Name/collision register and system-wide ownership census.
2. Existing recipe and adjacent-system overlap map.
3. Neutral Software Recipe Model specification and schema.
4. Read-only extraction and provenance fixtures.
5. Deterministic classification baseline.
6. Separate evaluation of classification, similarity, retrieval, impact analysis, and composition.
7. CRG/registry/DoE adapters only where their owners approve the contracts.
8. Bounded experiments with explicit stop states and independent evaluation.
9. Separate safety admission before any untrusted recipe execution.

## Non-goals

- No premature system or Brain ownership assignment.
- No renaming or changing existing systems to make room for this work.
- No reimplementation of Repo Replay, Commit Replay, CRG, CEEL, DoE, Delphi, Name Forge, or existing orchestration.
- No autonomous execution, secret access, external writes, provider spending, merge, deploy, or production routing.
- No claim that a candidate name is trademark-, package-, domain-, or repository-cleared.

See [NAME-COLLISION-REGISTER.md](NAME-COLLISION-REGISTER.md), [ARCHITECTURE-RECON.md](ARCHITECTURE-RECON.md), and [SOURCE-ADOPTION-MATRIX.md](SOURCE-ADOPTION-MATRIX.md).
