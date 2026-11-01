---
type: object
cluster: knowledge
universe: live
status: verified
entity: docs/ops/ui-surface-registry.json
verified_at: 2026-11-01
---

# UI Surface Registry

The **UI Surface Registry** is the repository's evidence-backed inventory of user-facing modality families and their renderer lanes; its map and JSON contract remain authoritative, while this card routes ICM readers to them.

## Why this shape

The repository has multiple user-facing projections and implementation approaches. Keeping surface family, renderer/framework, implementation evidence, and runtime conformance distinct avoids implying that a repository path proves a supported or deployed product.

## Shape

- `docs/ops/UI-SURFACE-VERSION-LANE-MAP.md` owns the modality taxonomy, renderer lanes, version identity fields, and conformance/release gates.
- `docs/ops/ui-surface-registry.json` owns the evidence-backed inventory and explicit unknown/proposed entries.
- `docs/ops/ui-surface-registry.schema.json` defines the Draft 2020-12 registry contract.
- `scripts/validate-ui-surface-registry.py` validates schema, identity uniqueness, evidence-path safety/existence, and the proposed/unknown boundaries.
- `.github/workflows/ui-surface-registry.yml` runs the focused registry validator and regression test.

Citations: `docs/ops/UI-SURFACE-VERSION-LANE-MAP.md` (sections 8–9); `docs/ops/ui-surface-registry.json`; `docs/ops/ui-surface-registry.schema.json`; `scripts/validate-ui-surface-registry.py`.

## Connected to

- **owns:** ICM routing for the user-facing surface taxonomy and its evidence-backed inventory.
- **owned-by:** the operations map, JSON registry/schema, validator, and focused CI workflow.
- **joins:** product surface questions to renderer choice, implementation evidence, independent version identities, and runtime conformance requirements.
- **looks-like-but-is-not:** proof of production deployment, runtime support, device testing, or a second canonical registry inside ICM.

## If you change this

- **Hits:** the canonical map/registry/schema, focused validator and tests, the root README navigation row, SHE dashboard index, and this ICM route when their contracts or entry points change.
- **Does not hit:** application runtime behavior, deployment configuration, device operations, or readiness claims merely because an evidence path exists.

## Surfaces

| Surface | Role |
|---|---|
| UI surface map | Defines families, rendering lanes, version identity, and conformance expectations. |
| JSON registry and schema | Maintain structured inventory and its contract. |
| Validator and CI | Check structural consistency and repository evidence paths. |
| ICM card/indexes | Route editors to the canonical source without copying the registry payload. |

## See

- Source: [UI Surface & Version-Lane Map](../../../ops/UI-SURFACE-VERSION-LANE-MAP.md)
- Source: [UI surface registry](../../../ops/ui-surface-registry.json)
- Source: [Registry JSON Schema](../../../ops/ui-surface-registry.schema.json)
- Source: [Registry validator](../../../../scripts/validate-ui-surface-registry.py)
- Source: [Focused registry workflow](../../../../.github/workflows/ui-surface-registry.yml)
