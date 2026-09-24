# Briefing Ingest and Resource Registry

The briefing system is an evidence-preservation pipeline.

## Resource record
A resource record preserves:
- canonical URL
- title
- publisher/project
- source type
- published/updated date
- observed_at
- version/commit/release
- license when relevant
- evidence_status
- horizon
- confidence
- claims
- unresolved_questions
- related_lanes
- related_projects
- provenance notes

## Evidence status
- confirmed: primary source directly establishes the fact
- research: paper/preprint/benchmark result
- attributed: claim belongs to an identified party
- signal: early/weak evidence
- speculative: hypothesis or forward-looking concept
- disputed: credible conflicting evidence exists

## Ingestion rules
1. Prefer primary sources.
2. Preserve the exact canonical source.
3. Never overwrite an older observation; append a new observation.
4. Keep raw source metadata separate from analyst interpretation.
5. Store dates in UTC ISO-8601.
6. Pin software evidence to a release, tag, or commit when available.
7. Record confidence and unresolved questions when material.
8. Deduplicate by canonical URL + version/commit where possible.

## Five-item briefing contract
Each item contains:
headline, horizon, evidence_status, summary, why_it_matters, opportunity_or_procurement, monorepo_relevance, sources, confidence, unresolved_questions, image_query.

The image is contextual enrichment only; it is never evidence.
