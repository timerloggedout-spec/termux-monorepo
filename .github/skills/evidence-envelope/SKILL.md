# Evidence Envelope Skill

## Purpose
Provide one normalized, provenance-first record for cross-system observations used by reconciliation, MVT, recovery, and promotion.

## Contract
Every observation MUST preserve:
- `experiment_id`
- `source`
- `source_id`
- `commit_sha` when applicable
- `baseline_sha` when applicable
- `observed_at`
- `event_at` when known
- `status`
- `outcome`
- `provenance`
- `confidence`
- `supersedes` when applicable

## Rules
1. Resolve refs to immutable SHAs before comparison.
2. Never infer timestamps or counts from prose when the provider API can supply them.
3. Distinguish provider/deployment failure from repository correctness.
4. Preserve raw evidence before deleting or regenerating derived artifacts.
5. A stale observation cannot satisfy a current-SHA gate.
6. Unknown provenance remains `unknown`; do not manufacture lineage.

## Consumers
GitHub Actions, Hex experiments, Linear execution records, Notion cockpit pages, Vercel deployment evidence, forensic recovery, and MVT cohorts.
