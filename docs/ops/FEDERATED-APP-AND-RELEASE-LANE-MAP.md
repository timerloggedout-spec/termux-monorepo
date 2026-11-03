# Federated Application & Release-Lane Map

**Status:** evidence-backed application seed plus exhaustive repository discovery census  
**Authority:** Termux monorepo system map; application repositories and release records remain authoritative for implementation and release facts.

## Purpose

Some product applications are organized outside the Termux monorepo, with independent AppIDs, UI/UX surfaces, repositories, and release lanes. They remain part of the Termux system architecture and must remain discoverable through its mappings.

The monorepo is the federation and relationship index, not the mandatory physical home of every application's code.

## Identity domains — do not conflate

| Identity | Answers | Examples |
|---|---|---|
| Product AppID | Which independently addressable application is this? | Fleet APK; ArchWiz APK |
| Repository identity | Where is its source governed? | owner/repository + default ref |
| UI surface ID | Which user-facing modality/surface does it expose? | fleet.android |
| Release-lane ID | Which independently versioned delivery channel is this? | fleet.android.apk |
| GitHub App ID | Which automation actor authenticates to GitHub? | Swarm 5560920; Collector 5535733 |
| Build/deployment identity | Which immutable build or deployment produced an artifact? | workflow run, artifact digest, deployment receipt |

A GitHub App numeric ID is not a product AppID. Neither should be inferred from a package name, repository name, workflow name, or release tag.

## Federated architecture

    Termux Monorepo — system map / registry / ICM / evidence routing
           |
           +-- product AppID registry
           |      +-- app -> owning repository/ref
           |      +-- app -> UI surface IDs
           |      +-- app -> independent release lanes
           |      +-- app -> dependencies / integration / ingestion edges
           |
           +-- automation identity registry (separate namespace)
           |
           +-- evidence & provenance index
                  ^                 ^
           external app repos   GitHub App workflows
           releases/tags        run/artifact/installation evidence

## Current evidence-backed records

| Application | Repository organization | UI surface | Release lane | Evidence state |
|---|---|---|---|---|
| Termux Fleet APK | Monorepo | fleet.android | fleet.android.apk | First release apk-v0.1.0; ephemeral-debug signing, not production signing |
| ArchWiz APK | Separate application identity; exact owning repo not established | archwiz.android | archwiz.android.apk | Separate from Fleet APK; package/tag/signing/build specifics remain unknown |

The ArchWiz_fork repository is a named reference/fork and is not assumed to be the owning ArchWiz APK repository. The owner's documented future ingestion direction is a planned relationship only; it does not collapse the two current applications.

The initial registry also records the GitHub App fleet in a distinct automation_identities collection. Those identities are automation actors, not user-facing products.

## Repository discovery census\n\n- [FEDERATED-APP-REPOSITORY-CENSUS.md](FEDERATED-APP-REPOSITORY-CENSUS.md) documents the census method and review queue.\n- [federated-app-repository-census.json](federated-app-repository-census.json) preserves all 714 unique repository records and 165 non-fork-named review candidates.\n- [Schema](federated-app-repository-census.schema.json) and [validator](../../scripts/validate_federated_app_census.py) enforce counts, uniqueness, owner scope, and the no-invented-AppID rule.\n- A repository name is a lead, not proof of a product; fork-named repositories are not automatically excluded.\n\n## Registry contract

Machine-readable source: federated-app-registry.json  
Schema: federated-app-registry.schema.json

Every application record carries a stable registry key and identity domain; product AppID only when established; organizational mode and owning repository identity (nullable until verified); UI surface references; independently identified release lanes, version authority, artifact types, signing state, and evidence; typed relationships with explicit status; and source links to authoritative records.

Every release lane is independently versioned. A change to one AppID's release cadence, artifact, or signing policy must not silently alter another AppID's version identity.

## Evidence and status semantics

- verified: directly supported by an authoritative repository record or release receipt.
- candidate: a lead for investigation, not an assertion.
- planned: an explicitly recorded future relationship, not implemented behavior.
- not-established / unknown: no reliable evidence; do not fill by inference.
- A monorepo path proves repository presence only. It does not prove deployment, platform support, release readiness, or production signing.
- A release tag proves a named release identity; artifact digest and verification receipt are required to establish artifact integrity.
- An external repository is linked by immutable owner/repository identity and ref; never copy its source tree into the monorepo merely to make the registry complete.

## Update and validation rules

1. Register a product application when its independent identity is created; do not wait until its code is copied into the monorepo.
2. Record the owning repository and default ref from live repository metadata.
3. Register each release lane separately, with its own version authority and artifact/signing evidence.
4. Keep GitHub App IDs in automation_identities, never in product_app_id.
5. Add UI surface IDs as references; the surface registry remains the owner of modality/renderer capability.
6. Use typed relationship edges: depends-on, integrates-with, ingests-into, derived-from, publishes-to, shares-contract-with.
7. Preserve unknowns and historical evidence; do not rewrite past releases when a lane changes.
8. Validate duplicate app keys, product AppIDs, release lane IDs, automation IDs, malformed repository names, dangling surface IDs, and invalid relationship targets.
9. Changes to registry/schema/validator/tests trigger the focused CI workflow.
10. Promote only after relevant checks and system-level evidence are observed; a committed registry is not proof of a shipped UI or release.

## Integration points

- UI surface/version map: docs/ops/UI-SURFACE-VERSION-LANE-MAP.md (on its existing proposal branch until merged).
- SHE cockpit: expose applications, surfaces, release lanes, freshness, and evidence status as separate dimensions.
- ICM: route AppID/release questions to this map and JSON registry; owning source documents continue to own build/release procedures.
- GitHub App fleet: docs/icm/objects/platform/github-app-fleet.md and ops/github-apps/PROCESS.json.

## Open evidence gaps

- Exact AppID and owning repository for ArchWiz APK.
- RepoStory 5565297 is confirmed as a GitHub App automation identity installed on `timerloggedout-spec/repo-story`; `PROCESS.json` describes it as an entry-repository-scoped automation identity. It is not evidence of a product AppID.
- Adjudicate all 714 discovered repositories (165 non-fork-named review leads) against product identity, UI surface, ownership, and release evidence. Repository discovery is exhaustive for the captured search pages; product classification remains open.

## Safety

This registry is descriptive and read-only. It does not create applications, mint credentials, trigger releases, publish artifacts, alter GitHub App installations, or authorize future ingestion.
