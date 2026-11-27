# Shared Data Visualization

**Scope:** cross-system guidance for presenting metrics, snapshots, uncertainty, provenance, and freshness.

## Canonical references

- [Dashboard chart standard](../../ops/DASHBOARD-CHART-STANDARD.md)
- [SHE Dashboard PRD](../../ops/SHE-DASHBOARD-PRD.md)
- [SHE snapshot contract](../../ops/SHE-DASHBOARD-SNAPSHOT-CONTRACT.md)
- [Evidence Projection Surface](../../ops/EVIDENCE-PROJECTION-SURFACE.md)
- [Tribute Dashboard data feeds](../../../apps/tribute-dashboard/data/)

## Shared design concerns

| Concern | Design requirement |
|---|---|
| Provenance | Link displayed facts to their source contract or evidence record. |
| Freshness | Distinguish current, stale, delayed, and unknown data when the source exposes freshness. |
| Partial data | Preserve partial/unknown states instead of implying completeness. |
| Uncertainty | Preserve source confidence semantics; avoid visual certainty beyond the evidence. |
| Time | Display timestamps and windows according to the owning data contract. |
| Empty / error | Distinguish an empty result from a failed or unavailable source. |
| Comparability | Keep units, cohorts, and time windows explicit. |

The table records cross-system concerns. Actual thresholds, schemas, and visual encodings remain defined by each source contract.
