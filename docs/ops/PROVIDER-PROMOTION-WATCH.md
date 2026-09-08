# Provider Promotion Watch

This is operational metadata, not routing policy. Promotion claims must be revalidated against the live provider catalog before use.

## OX Alpha / OpenRouter

- Model: `stealth/ox-alpha`
- Provider: OpenRouter / Stealth
- Current observed price: `$0` input and `$0` output.
- OpenRouter public reporting: free access on the OpenRouter route was reported through **Monday, August 24, 2026**. The exact cutoff time is not published in the source reviewed here.
- OpenCode launch messaging separately described approximately one week from the August 20 launch, implying a later window around August 27; that is a different route/promotion and must not be substituted for OpenRouter's end date.
- Operational rule: treat **2026-08-24 as the OpenRouter watch deadline**, but continue polling the live catalog until the route actually changes.

## Felo

Felo's public LLM API exposes `GET /api/v1/models`. Public model discovery does not necessarily expose account-specific promotional pricing. Therefore the catalog classifies missing pricing as `unknown`, not `free`.

The `FELO_AI_API` credential can still be used for controlled account-capacity experiments. Account quota/trial status should be measured from actual invocation outcomes rather than inferred from model metadata.

## Required telemetry

Every promotion observation should record:

- `observed_at`
- provider
- model
- pricing classification
- source URL / API endpoint
- promotion identifier if available
- published start/end date or timestamp
- precision (`timestamp`, `date`, `approximate`, `unknown`)
- actual invocation outcome

Do not hardcode a promotional model into the router. Promotion metadata only changes experiment priority/eligibility; the catalog remains authoritative for model selection.

## Current evidence

OpenRouter's Stealth provider page currently lists Ox Alpha at `$0/M input` and `$0/M output` with a 1.05M context window. The public listing also states that the provider is anonymous during the preview. Re-check the live listing before every high-volume experiment.

See also #337 (continuous evaluation), #335 (time-series discovery), and #336 (repository-history reconstruction).
