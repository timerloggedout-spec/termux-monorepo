# SHE Dashboard Snapshot Contract

This directory is the machine-facing contract for a read-only dashboard projection. It intentionally contains no live credentials and no provider-dependent state.

## Snapshot

A published snapshot should contain:

```json
{
  "schema_version": "1.0",
  "snapshot_id": "<stable id>",
  "source_ref": "master",
  "source_sha": "<40-char sha>",
  "generated_at": "<ISO-8601>",
  "coverage": {
    "status": "PARTIAL_CONTINUATION_REQUIRED",
    "next_start_page": 2
  },
  "corpus": {
    "manifest_sha": "<blob sha>"
  },
  "ledger": {
    "status": "UNVERIFIED"
  },
  "metrics": {},
  "experiments": [],
  "learning": []
}
```

## Rules

- `source_sha` is mandatory.
- `generated_at` is mandatory.
- Coverage status is mandatory.
- `UNVERIFIED` is a valid state and must not be converted to `0`.
- Metrics without provenance remain unavailable/low-confidence.
- Snapshots are projections; the underlying corpus remains authoritative.
- Hex imports consume snapshots; they do not replace them.

## Intended consumers

- `she/dashboard` static/interactive UI;
- Vercel build;
- GitHub Pages build;
- Hex import/export adapter;
- DOE/MVT analysis jobs.

## Historical reconstruction

The SHE projection may use the repository-native temporal query surface for point-in-time or bounded change views. Use the immutable L2 snapshot as evidence; do not reconstruct historical state from the current L1 graph alone.

- Point-in-time: temporal_query --at TIMESTAMP
- Range: temporal_query --between START END
- Change events: temporal_query --changes-only --between START END
- Snapshot inventory: temporal_query --timeline

These queries are read-only projections. Coverage and provenance from the selected snapshot remain authoritative.

## FCE snapshot projection

The optional metrics.flywheel_compounding_efficiency projection may expose status (OBSERVED, PARTIAL, UNVERIFIED, or MISSING), method and observation_id, fce_raw and matched fce_vs_baseline/fce_delta when comparable, cohort_id, sample size, and evidence reference.

Every value must resolve to the canonical FCE record and the snapshot source SHA. Missing values remain absent/null; never render them as zero. Percentiles are cohort-local and must be labeled as such. FCE is read-only presentation, not a dispatch, merge, or promotion authority.
