# Briefing

## Current collaborator briefing

- [2026-10-04 Morning Foresight Briefing](2026-10-04-collaborator-brief.md)
- [2026-10-04 machine-readable ingest](2026-10-04-collaborator-ingest.json)

## Contracts

- [Daily Digest Specification](DAILY-DIGEST-SPEC.md)
- [Briefing Ingest](../research/BRIEFING-INGEST.md)
- [FOSS Procurement Matrix](../research/FOSS-PROCUREMENT-MATRIX.md)
- [Foresight Radar](../research/FORESIGHT-RADAR.md)
- [Source Registry](../../config/foresight_digest_sources.json)

The briefing is append-only evidence work. Preserve source date/version/commit, evidence status, horizon, confidence, unresolved questions and provenance. Images are contextual enrichment only and never evidence.

## Citation and contributor provenance

- [Source Citation Index](SOURCE-CITATION-INDEX.md) — curated URLs from dated daily briefs, source/resource/procurement/radar JSONL, and related operations documentation.
- [BIUDL execution and provenance](../ops/BIUDL-EXECUTION-AND-PROVENANCE.md) — phases, author attribution, collaborator roles, security boundaries, and acceptance criteria.
- Offline citation extraction: `python3 scripts/ci/curate_briefing_sources.py --output data/briefing/source-citations.jsonl`.
- Author telemetry schema: [AGENT-THROUGHPUT-EVENT.schema.json](../ops/AGENT-THROUGHPUT-EVENT.schema.json).

The citation index is a navigational inventory, not a statement that every URL was re-fetched during generation. Claims retain the evidence status and confidence recorded by the source material.
