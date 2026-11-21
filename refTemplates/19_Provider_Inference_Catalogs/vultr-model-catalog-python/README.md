# vultr-model-catalog-python

Python SDK reference for Vultr Inference's public model catalog.

- Upstream: https://github.com/vultr/model-catalog-python
- Inspected revision: `4a414ab26e1f596cb98b3974a7d12182bf62dab3`
- License: MIT; verified from the pinned revision's `LICENSE`
- Runtime: Python 3.11+
- Runtime dependencies: none, per upstream README

## Relevant patterns

- `fetch_catalog` exposes the raw catalog payload.
- `load_catalog` normalizes records and exposes `network`, `cache` and `stale-cache` source states.
- `parse_catalog` isolates malformed entries as issues while preserving valid entries.
- `CatalogModel` retains modality-specific input/output specifications, exact pricing strings, reasoning support, tool and structured-output support, readiness and deprecation metadata.
- Shared normalized fixtures anchor parity with the TypeScript implementation.

Reference-only record. See [SOURCE.txt](SOURCE.txt) and [metadata.json](metadata.json).
