---
type: object
cluster: knowledge
universe: live
status: verified
entity: README.md
verified_at: 2026-08-17
---

# Navigation and Indexes

The **Navigation and Indexes** surface is the monorepo’s orientation layer: the root README owns the navigation ladder, while ArchWiz hubs and mapper outputs provide progressively deeper, sometimes generated, views.

## Why this shape

The repository is too large for folder crawling. The root navigation ladder intentionally routes from concise tool and concept catalogs to reference hubs, procedures, recovery material, and full ecosystem maps.

## Shape

- `README.md` names the navigation SSOT and routes common editor tasks to history, impact, change, validation, index rebuild, and cockpit entry points.
- `archwiz/TOOL_INDEX.md`, `CONCEPT_INDEX.md`, and `REFERENCE_HUB.md` are the preferred operational catalogs.
- `workspace/llm_map` contains richer mapper outputs and must be treated as a downstream reference rather than a hand-maintained replacement specification.

Citations: `README.md:71-98`, `README.md:112-195`, `archwiz/TOOL_INDEX.md:1-57`.

## Connected to

- **owns:** root navigation and the distinction between high-level catalogs and deeper maps.
- **owned-by:** `README.md` and the cited ArchWiz/index sources.
- **joins:** edit requests to the correct tool, architecture source, or generated mapping artifact.
- **looks-like-but-is-not:** a promise that every file in `workspace/llm_map` is current or safe to edit by hand.

## If you change this

- **Hits:** the relevant owning README, hub, catalog, or generator path and the links that intentionally point to it.
- **Does not hit:** source behavior in a subsystem merely because its name appears in a navigation table.

## Surfaces

| Surface | Role |
|---|---|
| Root README | Maintained navigation and live-project orientation. |
| ArchWiz catalogs | Compact operational routing. |
| Mapper outputs | Deep, generated or index-backed reference material. |
| Agent or developer | Selects the smallest relevant source set before editing. |

## See

- Source: [`README.md`](../../../../README.md)
- Source: [`archwiz/TOOL_INDEX.md`](../../../../archwiz/TOOL_INDEX.md)
