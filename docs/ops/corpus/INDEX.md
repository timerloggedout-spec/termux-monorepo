# Corpus Index

This directory defines the machine-readable contract for the repository's longitudinal evidence corpus.

| Surface | Role |
|---|---|
| `workspace/llm_map/context_relationships/` | Canonical metadata-only historical relationship substrate |
| `PR-OBSERVATION.schema.json` | Schema for compact per-PR observation projections |
| `EXPERIMENT.schema.json` | Schema for DOE/MVT candidate/baseline experiment records |
| `LEARNING.schema.json` | Schema for experiment-derived learning records |
| `../ACTION-EFFECT-EVENT.schema.json` | Temporal action→effect event contract |
| `../EVIDENCE-ENVELOPE.schema.json` | Evidence envelope / provenance contract |
| `../ACTION-EFFECTIVENESS-LEDGER.md` | Measurement semantics and state distinctions |
| `../../evaluations/swe-performance/` | DOE/MVT evaluation and cohort surfaces |

## Data flow

`history → corpus → observation → experiment cohort → evaluation → learning → manager evolution`

The corpus is append-oriented in meaning even when the checked-in canonical index is rebuilt. Historical records are retained by the compiler/backfill process rather than overwritten by a narrow current-state snapshot.

## Completion

The current canonical relationship snapshot is intentionally bounded. See its `manifest.json` and `build-summary.json` for the exact collection window and `history_window.next_start_page`.

A complete backfill is reached only when the continuation state is `null` for the complete declared history.
