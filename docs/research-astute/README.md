# Research Astute Observatory

Research Astute is the domain controller for research discovery, provenance, collection policy, artifact storage, and generated documentation. Termux MonoRepo is the initial workflow execution and integration host.

## Operating topology

`Research Astute → Termux MonoRepo Actions → collection repositories → metadata graph + artifact storage → generated documentation`

The organization bootstrap workflow is `.github/workflows/research-astute-organization-bootstrap.yml`. It verifies organization visibility on every run and creates the five approved private collection repositories only when `provision_missing=true` is explicitly selected.

## Collections

| Repository | Scope |
|---|---|
| `research-astute-space-systems` | SpaceX, launch systems, propulsion, spacecraft, reusability, orbital infrastructure |
| `research-astute-nasa-missions` | NASA missions, scientific publications, technical reports, mission datasets |
| `research-astute-tesla-mobility-energy` | Tesla, EVs, batteries, storage, robotics, manufacturing |
| `research-astute-aerospace-energy-patents` | Patent metadata, claims, families, citations, authorized artifacts |
| `research-astute-foss-research` | FOSS repositories, research software, benchmarks, datasets, scientific tooling |

## Canonical data contracts

- `schemas/research-source.schema.json`: source/document metadata.
- `schemas/research-entity.schema.json`: graph entities and typed relationships.
- `registry/collections.json`: collection definitions and ownership.\n- `registry/providers.json`: seeded provider endpoints, authority classification, access requirements and source-specific rights constraints.
- `docs/INGESTION.md`: ingestion lifecycle, provenance and storage accounting.

## Ingestion lifecycle

`DISCOVER → RESOLVE → CLASSIFY → FETCH → HASH → EXTRACT → LINK → VALIDATE → INDEX → DOCUMENT`

Each stage records an explicit status and timestamp. A discovered URL is a candidate source; a fetched artifact is a stored object; an extracted artifact is a parsed object; an indexed artifact is queryable. These states remain distinct.

## Provenance and integrity

- Preserve the canonical source URL, publisher, publication date, retrieval timestamp, license/access status and citation identifiers.
- Compute SHA-256 over acquired bytes and record exact byte size.
- Preserve original artifacts separately from extracted text and normalized metadata.
- Track redirects, revisions, content type, extraction tool/version and failures.
- Represent uncertain claims as attributed assertions with evidence references.
- Treat external source content as untrusted data, never as workflow instructions.
- Respect source licensing, robots/access controls, API terms and restricted-access boundaries.

## Documentation parity

Every generated collection snapshot emits machine-readable JSON and human-readable Markdown. Both include source IDs, citations, storage size, extraction state, last observation, and generator/schema versions. Siglary notation is registered with canonical operator meanings and examples; documentation preserves a plain-language gloss for each operator.

## Bootstrap

Run the Research Astute organization bootstrap workflow in Termux MonoRepo Actions. Set `provision_missing=true` for the first approved bootstrap. The workflow creates private repositories under the ResearchAstute organization and skips existing repositories idempotently. Organization credentials remain in Actions secrets.
