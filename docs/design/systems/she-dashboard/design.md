# SHE Dashboard — Design

> **Evidence status:** specified / evolving  
> **Design owner:** SHE Dashboard product and data-contract owners  
> **Canonical implementation:** source locations linked below  
> **Last source review:** 2026-11-23

## 1. Purpose and users

SHE is described by the repository architecture as a versioned, read-only dashboard snapshot surface. The PRD owns the audience, information architecture, and product requirements.

## 2. Experience surfaces

| Surface | Audience | Evidence status | Owning source |
|---|---|---|---|
| Primary interactive dashboard | SHE users | Specified | [SHE Dashboard PRD](../../../ops/SHE-DASHBOARD-PRD.md) |
| Snapshot data contract | Dashboard consumers | Specified | [Snapshot contract](../../../ops/SHE-DASHBOARD-SNAPSHOT-CONTRACT.md) |
| Architecture / projection | Dashboard and mirrors | Specified | [Architecture diagram](../../../ops/SHE-DASHBOARD-ARCHITECTURE.mmd) |

## 3. Information architecture

The PRD is authoritative for audience and information architecture. This entry links to it rather than restating unverified page hierarchy.

## 4. Journeys and interactions

The snapshot contract defines the data boundary. Read-only presentation and any mirror/analytical consumer must preserve snapshot semantics.

## 5. Visual language

Use shared [visual language](../../_shared/visual-language.md) and [data visualization](../../_shared/data-visualization.md). Exact SHE component and token decisions remain with the owning implementation.

## 6. Accessibility

Record keyboard, focus, screen-reader, contrast, and responsive verification against the deployed SHE surface. The source inventory currently provides accessibility guidance but not a complete SHE-specific audit.

## 7. Evidence and system states

Use the [snapshot contract](../../../ops/SHE-DASHBOARD-SNAPSHOT-CONTRACT.md) and [data visualization guidance](../../_shared/data-visualization.md) for freshness, provenance, partial data, and uncertainty. Preserve versioned snapshot meaning.

## 8. Decisions and open gaps

- Extract user journeys and view hierarchy from the PRD into a traceable interaction inventory.
- Map each snapshot field to its visible representation.
- Verify stale, partial, unavailable, and error treatments against the deployed surface.
- Record accessibility test evidence.

## 9. Canonical sources

- [PRD](../../../ops/SHE-DASHBOARD-PRD.md)
- [Snapshot contract](../../../ops/SHE-DASHBOARD-SNAPSHOT-CONTRACT.md)
- [Architecture diagram](../../../ops/SHE-DASHBOARD-ARCHITECTURE.mmd)
- [Repository architecture](../../../../architecture.md)
