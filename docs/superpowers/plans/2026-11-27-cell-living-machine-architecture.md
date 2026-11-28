# CELL: THE LIVING MACHINE — Architecture Plan

> **For agentic workers:** Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Each task ends with a verifiable artifact and a reviewable commit.

**Goal:** Establish a source-grounded project profile and a three-plane research/development architecture for an original molecular-to-cellular simulation game.

**Architecture:** A dedicated game repository owns the playable product. Termux MonoRepo owns the project profile, lanes, standards, specialist routing, and integration contracts. Research Astute holds reusable research references; Search Astutely coordinates search snapshots and result aggregation; scientific databases remain authoritative upstream sources. Cross-repository integration uses versioned manifests, immutable source references, and API contracts.

**Tech Stack:** YAML project manifests, JSON Schema, GitHub proposal registry, research-seed intake, versioned external database APIs, game-engine selection after prototype requirements.

**Spec:** `docs/proposals/active/cell-the-living-machine/MANIFEST.md`

## Global Constraints

- Reuse the existing Game Development & Production, Game Player Machines & Genre Teams, Game QA & Accessibility, and Game ML Research lanes.
- Keep game development, player execution, QA verdicts, and scientific research as distinct responsibilities.
- Record every external source with stable identifiers, observed version/date, attribution, usage terms, and provenance.
- Use one knowledge corpus with multiple resolution lenses; age remains outside the progression model.
- Treat predictions, experimental structures, curated annotations, educational abstractions, and gameplay approximations as distinct evidence classes.
- Pin engine, tools, dependencies, and assets when the prototype selects them.
- Keep iJEP Studio media and 3D assets in a reference-only state until usage rights are documented.
- Keep credentials in approved secret storage; project manifests contain secret names and scope metadata only.
- Use feature branches, bounded commits, proposal item references, and repository verification gates.

## Review Focus

- Cross-repository identity drift — stable repository IDs and canonical URLs resolve to the same project.
- Research-source license ambiguity — each asset/data source has a usage disposition before packaging.
- Predicted-versus-experimental structure confusion — every structure carries an evidence class and confidence context.
- Specialist depth and audience accessibility — every lens reaches the same underlying knowledge with a different explanatory resolution.
- Database version drift — imported records retain upstream release, accession, retrieval date, and checksum.

---

### Task 1: Establish project profile control plane

**Files:**
- Create: `.config/llm_map/profiles/projects/cell-the-living-machine.json`
- Create: `ops/projects/manifests/cell-the-living-machine.yaml`
- Create: `ops/projects/registry.yaml`
- Create: `ops/projects/registry.schema.json`
- Create: `ops/projects/README.md`
- Reuse: `ops/projects/profile.schema.json` (`project-profile/v1`)

**Interfaces:**
- Consumes: existing game-lane taxonomy, anchored entity references, research-seed intake.
- Produces: stable `project:cell-the-living-machine` identity and a profile resolvable from MonoRepo.

- [ ] Define the project registry as an index of profile references, repository identity, lane assignments, and lifecycle state.
- [ ] Define the profile schema with authority, repositories, research planes, game facets, lenses, specialists, tools, QA, and release metadata.
- [ ] Register the project as `proposed`; set game repository provisioning to `pending`.
- [ ] Validate YAML and JSON Schema with the repository's available validation path.
- [ ] Commit the profile control-plane slice.

### Task 2: Record the three-plane integration architecture

**Files:**
- Create: `docs/proposals/active/cell-the-living-machine/PROJECT_PROFILE.yaml` (review pointer to canonical scope profile and manifest)
- Create: `docs/proposals/active/cell-the-living-machine/source.md`

**Interfaces:**
- Consumes: Research Astute repository evidence, Search Astutely organization evidence, MonoRepo lane contracts.
- Produces: source-of-truth map and explicit integration states.

- [ ] Record Research Astute as a reusable research-reference plane with license review metadata.
- [ ] Record Search Astutely organization and candidate repositories with connector/endpoint status.
- [ ] Record MonoRepo as the developer orchestration and tooling plane.
- [ ] Record the dedicated game repository as a provisioning target with repository creation as a tracked dependency.
- [ ] Commit the architecture and evidence map.

### Task 3: Map scientific databases and identifiers

**Files:**
- Create: `docs/proposals/active/cell-the-living-machine/RESEARCH_MAP.yaml`
- Create: `docs/proposals/active/cell-the-living-machine/DATA_SOURCES.yaml`

**Interfaces:**
- Consumes: official RCSB PDB, EMDB, AlphaFold DB, UniProt, NCBI, Reactome, ChEBI, and literature API documentation.
- Produces: domain-indexed source catalog and identifier crosswalk plan.

- [ ] Map structure, sequence, annotation, pathway, chemistry, imaging, and literature sources.
- [ ] Define accession crosswalks across PDB, UniProt, NCBI, AlphaFold, EMDB, and literature identifiers.
- [ ] Record API mode, license/terms review, attribution, versioning, rate policy, and data freshness per source.
- [ ] Separate experimental coordinates, predicted models, curated annotations, and educational representations.
- [ ] Commit the source catalog.

### Task 4: Define game taxonomy and knowledge lenses

**Files:**
- Create: `docs/proposals/active/cell-the-living-machine/CONTENT_TAXONOMY.yaml`
- Create: `docs/proposals/active/cell-the-living-machine/GAME_DESIGN.md`

**Interfaces:**
- Consumes: iJEP Studio channel inventory as a seed, scientific source map, existing game genre taxonomy.
- Produces: genre facets, content graph, mechanics, and lens contract.

- [ ] Define the game as a hybrid of simulation, systems strategy, exploration, puzzle, and progression RPG facets.
- [ ] Define Field, Mechanism, Quantitative, Structural, and Research lenses over one shared knowledge graph.
- [ ] Make challenge settings alter constraints, uncertainty, resource budgets, and scenario complexity.
- [ ] Define molecular, membrane, organelle, cell, tissue, and organism scales as linked views.
- [ ] Commit the content and design contract.

### Task 5: Establish provenance and rights gates

**Files:**
- Create: `docs/proposals/active/cell-the-living-machine/PROVENANCE.md`

**Interfaces:**
- Consumes: source catalog, iJEP Studio public materials, scientific database terms.
- Produces: per-asset and per-claim provenance contract.

- [ ] Define source classes, citation fields, version pins, checksums, and review status.
- [ ] Record iJEP Studio media as inspiration/reference material pending a specific usage license.
- [ ] Define review requirements for 3D models, footage, posters, structures, images, sound, and educational derivatives.
- [ ] Commit the provenance contract.

### Task 6: Review and open integration PR

**Files:**
- Modify: `docs/proposals/registry.yaml`
- Create: proposal package and project registry artifacts above.

- [ ] Verify branch ancestry and changed-file scope.
- [ ] Run available YAML/JSON checks and inspect the complete diff.
- [ ] Open a pull request with all implemented item IDs.
- [ ] Record repository-gate and Termux-smoke evidence when execution environment access is available.
- [ ] Keep game-repository provisioning and Search Astutely connection as explicit external dependencies until their authorized actions complete.

## Work Package Map

| Package | Lane | Deliverable |
|---|---|---|
| CLM-01 | Orchestration & Quality Control | Project registry, profile schema, project profile |
| CLM-02 | Research & Intelligence | Research Astute / Search Astutely source map |
| CLM-03 | Research & Intelligence | Molecular database and identifier crosswalk catalog |
| CLM-04 | Game Development & Production | Genre facets, game design, knowledge-lens contract |
| CLM-05 | Game QA & Accessibility | Science integrity, accessibility, provenance review |
| CLM-06 | Delivery Reliability / CI-CD | Validation, PR, gates, release evidence |

## Verification Ladder

- V0 — manifest shape, schema validation, stable IDs, link integrity.
- V1 — representative source retrieval and identifier crosswalk checks.
- V2 — prototype build, runtime traces, deterministic scenario tests.
- V3 — independent science review, accessibility review, performance and release checks.

## Current Execution Boundary

This plan covers architecture and documentation. Playable implementation begins after project-profile review, game-repository provisioning, engine selection, and the first source-backed content slice.
