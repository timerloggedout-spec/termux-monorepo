# Skills index (recon 2026-11-18)

This is an index, not a clone. Full skill content is about 12.87 MB across 1,227 files, averaging about 10.5 KB each. Connector tools carry content through tool arguments, so a full byte-for-byte clone isn't feasible from here. This index records what exists so it can be found and routed.

## Totals

- SKILL.md files: 1,227
- Total size: 12.87 MB (average 10.5 KB)
- Namespaces: 1,150 plugin directories

## By namespace

| Namespace | SKILL.md count | Notes |
|---|---|---|
| UUID-namespaced vendor plugins | 969 | Auto-generated plugin folders |
| qdrant-skills | 61 | Qdrant vector database guidance |
| examples | 35 | Example and reference skills |
| cockroachdb | 34 | CockroachDB operations |
| figma | 16 | Figma design tooling |
| engineering | 10 | Engineering workflows |
| data | 10 | Data analysis workflows |
| product-management | 9 | Product workflows |
| operations | 9 | Operations workflows |
| legal | 9 | Legal workflows |
| public | 8 | Core document and design skills (docx, pdf, pptx, xlsx, and others) |
| marketing | 8 | Marketing workflows |
| finance | 8 | Finance workflows |
| design | 7 | Design workflows |
| bio-research | 6 | Bioinformatics workflows |
| pdf-viewer | 5 | PDF viewing and annotation |
| enterprise-search | 5 | Search across connected sources |
| datadog | 5 | Datadog tooling |
| productivity | 4 | Task and memory management |
| base44 | 4 | Base44 app building |
| miro | 3 | Miro boards |
| pendo-orchestrate | 1 | Pendo journeys |
| pendo-guides | 1 | Pendo in-app guides |

## Routing rule

Use the namespace to find a family, then read its SKILL.md directly. Do not load every skill for one task. For a document, start with public/docx, public/pdf, public/pptx, or public/xlsx.

## Clone options (not done)

1. Run a sync from a machine that holds the plugin sources (a laptop or a server with the marketplace), then commit the result.
2. Keep this index, and load each skill from its source when needed.
3. Commit the families that matter most (qdrant-skills, cockroachdb, figma, public) as separate commits. Each is well under the size limit for one call.
