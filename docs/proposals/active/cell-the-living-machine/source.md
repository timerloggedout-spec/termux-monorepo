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

## Research Astute

- Repository: https://github.com/NDuma/ResearchAstute
- README: description remains in progress; Biology section lists PhyloAnnotator, a Mittweida resource, and SimTK.
- `resources_tools.md`: short Biology resource list with those three links.
- LICENSE: contains an open licensing discussion followed by Apache License 2.0 text. The intended license and file coverage require owner confirmation before content reuse.
- Integration status: reference discovery available; automated ingestion and reusable-content rights pending review.

## Search Astutely

- Organization: https://github.com/search-astute-ly
- Candidate repositories visible through GitHub search:
  - https://github.com/search-astute-ly/termux-monorepo_enterprise
  - https://github.com/search-astute-ly/termux-monorepo_enterprise_too
  - https://github.com/search-astute-ly/redesigned-octo-rotary-phone
  - https://github.com/search-astute-ly/manus-public-ui-research
- The two Enterprise-named repositories are accessible to the connected GitHub identity with admin/push permissions in repository search results. Their inspected README surfaces describe Termux recovery and developer environment planning; a canonical search-aggregation API and result store remain unverified.
- The requested plugin reference `Plugin_60aea7460bd4819199fd97a9553a5e12` returned `plugin_not_found` from plugin dependency lookup. Plugin discovery for the name/capability surfaced Scite, Firecrawl, Notion, and other adjacent services; a Search Astutely connector remains unverified.
- `AsAstraNeoNexus` is absent from the connected GitHub repository/owner search performed for this pass. Account ownership, Enterprise trial status, migration state, and the account-header deletion notice require direct account/organization settings review by the owner.
- Integration status: organization identity verified; service endpoint, canonical data repository, connector, account relationship, and migration state pending verification.

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
