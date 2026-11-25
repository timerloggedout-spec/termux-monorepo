# ITEMS — research-astute-observatory

| ID | Item | State | Evidence / next action |
|---|---|---|---|
| RAO-001 | Establish domain-controller and execution-host topology | done | docs/research-astute/README.md |
| RAO-002 | Define source metadata schema | done | docs/research-astute/schemas/research-source.schema.json |
| RAO-003 | Define graph entity and relationship schema | done | docs/research-astute/schemas/research-entity.schema.json |
| RAO-004 | Register five research collection repositories | done | docs/research-astute/registry/collections.json |
| RAO-005 | Add idempotent private organization bootstrap workflow | done | .github/workflows/research-astute-organization-bootstrap.yml |
| RAO-006 | Define ingestion, provenance, access and storage lifecycle | done | docs/research-astute/INGESTION.md |
| RAO-007 | Register proposal in proposal lifecycle registry | executing | Validate registry gate on PR |
| RAO-008 | Add schema validation and deterministic documentation generator | queued | Implement tests and generator |
| RAO-009 | Seed provider registry with source authority, API access and rights constraints | done | docs/research-astute/registry/providers.json; automated WIPO PATENTSCOPE access explicitly disabled by source terms |
| RAO-010 | Add source adapters: GitHub/FOSS, patents, papers, NASA and SpaceX/Tesla public surfaces | queued | Provider-specific adapters with rate limits and citations |
| RAO-011 | Add artifact object storage and graph backend adapters | queued | Select backend from current infrastructure inventory |
| RAO-012 | Add collection-level generated docs and storage manifests | queued | Human + machine parity |
| RAO-013 | Add Research Astute native monorepo and standalone workflow migration | queued | Future domain-owned execution phase |
| RAO-014 | Define full engineering-blueprint schema and request schema | done | docs/research-astute/schemas/engineering-blueprint*.schema.json |
| RAO-015 | Seed NASA, SpaceX and Tesla engineering-blueprint research requests | done | docs/research-astute/registry/engineering-blueprint-requests.json |
| RAO-016 | Build evidence-backed engineering maps for each seeded request | queued | Produce context, functional, logical, physical, interface, flow, lifecycle and assurance views |
