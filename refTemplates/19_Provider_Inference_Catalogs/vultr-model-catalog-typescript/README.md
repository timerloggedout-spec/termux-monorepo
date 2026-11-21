# vultr-model-catalog-typescript

TypeScript SDK reference for Vultr Inference's public model catalog.

- Upstream: https://github.com/vultr/model-catalog-typescript
- Inspected revision: `6e55057cb718213937c4c118271f5a2ca1779d0d`
- License: MIT; verified from the pinned revision's `LICENSE`
- Runtime: Node.js 20+ or Bun
- Runtime dependencies: none, per upstream README

## Relevant patterns

- `fetchCatalog` exposes the raw catalog payload.
- `loadCatalog` normalizes records and exposes `network`, `cache` and `stale-cache` source states.
- `parseCatalog` isolates malformed entries as issues while preserving valid entries.
- `CatalogModel` retains modality-specific input/output specifications, exact pricing strings, reasoning support, tool and structured-output support, readiness and deprecation metadata.
- `toCanonical` emits the shared snake_case form pinned by fixtures shared with the Python implementation.

Reference-only record. See [SOURCE.txt](SOURCE.txt) and [metadata.json](metadata.json).
