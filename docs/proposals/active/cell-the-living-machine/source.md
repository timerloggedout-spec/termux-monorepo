# Source reconnaissance — cell-the-living-machine

**Observed:** 2026-11-27  
**Branch:** `feature/cell-living-machine-architecture`  
**Scope:** project lanes, repository identities, reusable research, search aggregation, and molecular data authorities.

## MonoRepo evidence

- `docs/recon/team-formation/GAME_DEVELOPMENT_LANES.md` defines Game Development & Production, Game Player Machines & Genre Teams, Game QA & Accessibility, Game ML Research, and related specialist responsibilities.
- `docs/recon/team-formation/GAME_PLAYER_FLEET.md` defines additive genre-role families, game catalog fields, machine profiles, telemetry, reset evidence, and score events.
- `docs/recon/team-formation/GAME_DEVELOPMENT_TASK_CARD.yaml` and `schemas/game-development-context.schema.json` provide reusable task and context contracts.
- `docs/recon/team-formation/LABEL_TAXONOMY.md` defines additive lanes, teams, roles, skills, targets, machine profiles, game catalog, scorecards, and tool profiles.
- `docs/repositories/README.md` defines the Repository Observatory and research-seed progression. The current research-seed set is small and uses versioned JSON records.
- `ops/projects/profile.schema.json` already defines the ArchWiz `project-profile/v1` scope contract. `docs/ops/ARCHWIZ-CONCEPT-MAP.md` directs project profiles into a separate project-scope family under `.config/llm_map/profiles/projects/`, with scope over repositories, issue classes, lanes, and artifact stores.
- `docs/ops/RESEARCH-TRIGGERS.md` and `.github/ISSUE_TEMPLATE/research-service.yml` route research services into `docs/repositories/research-seeds/*.json`.

## Dedicated game repository

- Repository: https://github.com/timerloggedout-spec/cell-the-living-machine
- Provisioned through the existing MonoRepo Repository Provisioner workflow, run `46108047424`; workflow job and all four steps completed successfully.
- Repository ID: `1475194740`; owner: `timerloggedout-spec`; visibility: private; default branch: `main`.
- Seeded README, architecture, knowledge lenses, research/provenance, engine evaluation, decision log, project-control links, contribution guide, and license-decision record.

## Research Astute

- Organization: https://github.com/Research-Astute
- Signed-in GitHub account `timerloggedout-spec` is listed as an organization owner.
- Existing `manus-ui-research-hub` is an integration hub for public-source Manus UI research and deterministic development lanes. Its `.gitmodules` pins `search-astute-ly/manus-public-ui-research` and `Research-Astute/manus-ui-adapter-lab`.
- Existing `manus-ui-research-hub` and `manus-ui-adapter-lab` have a Manus UI / deterministic adapter scope. They provide an integration pattern; the molecular biology research store uses a dedicated repository.
- New reusable science repository: https://github.com/Research-Astute/molecular-biology-research
- Repository ID: `183701786`; visibility: private; default branch: `main`.
- Research contracts: `RESEARCH_ASTUTE_CONTRACT.yaml`; source registry seed: 26 candidate providers; initial mechanism dossiers: sodium-potassium pump, aquaporin, ATP synthase.
- The third-party `NDuma/ResearchAstute` repository is a separate public resource. Its license and ownership scope remain review-required; it is excluded from the canonical Research-Astute project plane.
- Integration status: owner organization and dedicated repository verified; curated record population and adapter workflow pending.

## Search Astutely

- Organization: https://github.com/search-astute-ly
- Signed-in GitHub account `timerloggedout-spec` is listed as an organization owner.
- The organization is linked to the `AdAstraNeoNexus` GitHub Enterprise account; organization lifecycle and service endpoint review remain owner-side tasks.
- The organization's `manus-public-ui-research` repository is scoped to public Manus UI source inventories, static assessments, license/provenance reviews, and synthetic fixtures. It serves as a research-lane example rather than a general scientific search service.
- Candidate repositories visible through GitHub search:
  - https://github.com/search-astute-ly/termux-monorepo_enterprise
  - https://github.com/search-astute-ly/termux-monorepo_enterprise_too
  - https://github.com/search-astute-ly/redesigned-octo-rotary-phone
  - https://github.com/search-astute-ly/manus-public-ui-research
- The two Enterprise-named repositories are accessible to the connected GitHub identity `timerloggedout-spec` with admin/push permissions in repository search results. Their inspected README surfaces describe Termux recovery and developer environment planning; a canonical search-aggregation API and result store remain unverified.
- The GitHub UI identifies `timerloggedout-spec` as an organization owner for both `Research-Astute` and `search-astute-ly`.
- The requested plugin reference `Plugin_60aea7460bd4819199fd97a9553a5e12` returned `plugin_not_found` from plugin dependency lookup. Plugin discovery surfaced adjacent research tools; a Search Astutely connector remains unverified.
- `AsAstraNeoNexus` remains unverified in the connected GitHub scope. Account ownership, Enterprise trial status, migration state, and the account-header deletion notice require direct account/organization settings review by the owner.
- The `manus-public-ui-research` repository describes a public userscript/library research lane; the inspected README gives it a separate scope from search aggregation. `redesigned-octo-rotary-phone` is a small placeholder-style repository with a README focused on placeholder-style content with search-service capability unverified.
- Integration status: organization identity verified; service endpoint, canonical data repository, connector, account relationship, and migration state pending verification.

## Scientific database map

- The initial catalog contains 26 candidate sources across structural biology, sequence/annotation, molecular interactions, pathways, chemistry, enzyme kinetics, cell models/expression, literature, and structural-biology education.
- Structural annotation candidates include RCSB PDB and PDBe-KB; interaction sources include IntAct/PSICQUIC, BioGRID, and STRING; kinetic sources include SABIO-RK, BRENDA, and Rhea; cell context includes Cellosaurus, Human Protein Atlas, and Expression Atlas.
- API and policy gates are source-specific: BioGRID uses a registered access key; STRING recommends version-specific endpoints, caller identity, and paced requests; BRENDA's online data uses CC BY 4.0 while SOAP access requires registration; SABIO-RK exposes REST services; Cellosaurus exposes a REST API; PDBe-KB exposes REST annotations; Rhea exposes REST and SPARQL access.
- Catalog entries remain candidates until sample retrieval, attribution, terms, rate policy, versioning, and provenance are verified.

## iJEP Studio

- Live channel record: 125 videos, 28K subscribers, approximately 4.57M views at observation time 2026-11-27.
- The uploads playlist returned 100 records on page one and 25 on page two; 125 unique video IDs were indexed in `research/ijep-studio-channel-inventory.json`.
- Indexed metadata: video ID, title, URL, publication metadata, duration, view count, thumbnail, and title-derived topic candidates. Playlist-level description fields were empty; per-video details and transcripts remain a follow-up.
- Channel: https://www.youtube.com/@iJEPStudio
- Official site: https://ijepstudio.com/
- Official site describes structural biology animation, scientific review, use of real structural references, and a production workflow involving structural data.
- Initial topic seeds include ATP synthase, aquaporin, sodium-potassium pump, ribosome, DNA replication, chromatin, molecular motors, and cellular processes.
- Inventory scope includes every video and short, title, description, duration, publication date, transcript where available, linked papers, PDB/EMDB accessions, source organisms, comments with technical value, and rights status.
- iJEP media and 3D assets carry reference-only status until the applicable license and permission are recorded.

## Architecture inference

The three-plane model preserves independent ownership and reuse:
1. Research Astute holds reusable research references and curated knowledge artifacts.
2. Search Astutely holds discovery runs, normalized search results, deduplication, source snapshots, and query lineage.
3. Termux MonoRepo holds development orchestration, project profiles, task routing, tool profiles, CI, QA, and release policy.
4. The game repository holds the playable product and versioned game-specific assets.
5. Scientific databases remain canonical upstream data authorities; the research planes index and reconcile their records.

This architecture is a proposal based on repository evidence and the user's stated responsibilities. Search Astutely service capabilities and Research Astute reuse rights remain pending direct verification. The project profile follows the existing ArchWiz scope schema; game-specific metadata lives in a linked project manifest.
