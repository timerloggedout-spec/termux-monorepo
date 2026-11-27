# Urdu Portal DOE campaign v1

State: registered_not_run.

## Before execution
- Verify provider/account support for Urdu and record the exact endpoint, region, model/version, quota, and pricing evidence.
- Pin source fixture revision, glossary revision, prompt revision, and reviewer rubric.
- Randomize treatment order per task and blind reviewers to provider identity.
- Run the human baseline on the same fixture cohort.
- Preserve failed, unavailable, skipped, and censored cells.

## Record layout

- DESIGN.json: pre-registered hypothesis, factors, cohort, outcomes, and promotion rule.
- records/<run-id>.json: one schema-valid observation per treatment/task.
- SUMMARY.json: generated aggregate, distributions, uncertainty, and treatment comparisons.
- RUBRIC.md: blinded human review anchors and reviewer protocol.

Schema: localization/schemas/experiment-record.schema.json.

## Analysis sequence

Screen factors → inspect interactions → replicate promising treatments → validate on a held-out cohort → recommend an adapter configuration. Keep the human baseline in every cohort. Quality leads the decision; cost and latency remain secondary operational outcomes.

Provider credentials enter through approved secret storage at execution time. The registry stores credential references only.
