# ICM System-Map Schema

This schema governs only `docs/icm/`. It does not impose file names or metadata on the source tree.

## Card types

| Type | Purpose | Required fields |
|---|---|---|
| `object` | A durable component, boundary, or documentation shelf. | `cluster`, `universe`, `status`, `entity` |
| `process` | A real, repeatable editor or runtime movement. | `universe`, `status`, `consumes`, `produces` |

## Field values

| Field | Allowed values | Meaning |
|---|---|---|
| `universe` | `live`, `leftover`, `ghost` | Whether the cited source is current, non-primary, or only named. |
| `status` | `verified`, `stub`, `stale` | `verified` requires a source path and line/date evidence; `stub` is a route without a completed card; `stale` is known to need re-verification. |
| `cluster` | `platform`, `operations`, `knowledge`, `governance` | The primary editing question the card answers. |

## Evidence rule

A `verified` claim must cite the owning repository path and line range where practical. The cited source remains authoritative. The map may summarize only the minimum needed for routing and first-order impact.

## Change-impact rule

Every verified object and process card names **Hits** and **Does not hit**. “Does not hit” must call out the obvious adjacent surface that is not automatically changed, preventing broad and unjustified edits.
