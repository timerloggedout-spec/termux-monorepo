# Briefing contract validation

The daily digest contracts are documented in `docs/briefing/DAILY-DIGEST-SPEC.md`,
`docs/research/BRIEFING-INGEST.md`, `docs/research/FOSS-PROCUREMENT-MATRIX.md`,
and `docs/research/FORESIGHT-RADAR.md`. The validator turns the machine-checkable
parts of those contracts into a deterministic, standard-library-only check.

## Run locally

```sh
python -m unittest tests.test_briefing_contract_validator
python scripts/ci/briefing_contract_validator.py \
  --briefing data/briefing/briefings/2026-09-30.json \
  --registry config/foresight_digest_sources.json
```

Pass `--briefing PATH` more than once to validate multiple dated snapshots.
The command exits non-zero for malformed JSON or contract violations and does
not modify source files.

## What is checked

- Canonical contract document paths and valid briefing date / UTC generation time.
- One to five items, each with the required summary, action, relevance, source,
  horizon, evidence status, confidence, unresolved-question, and image-query fields.
- Allowed horizon and evidence-status vocabulary from the repository contracts.
- Absolute HTTP(S) source URLs and non-empty source provenance types.
- Registry schema version, required resource metadata, valid URLs, and unique IDs.

## Deliberate limits

This is structural validation, not a truth oracle. It does not fetch URLs, verify
claims, determine source authority, calculate confidence, judge whether an item
is substantive, or treat an image as evidence. Horizon and confidence remain
separate dimensions. It does not claim any target is portable without a real
target-specific test. CI wiring should be added to the repository's existing
required-check path after confirming its current workflow entry point.
