# Help-Wanted realization evidence registry

This registry is the explicit ingestion boundary for downstream effect evidence. A merge, closed PR, claim comment, test result, or self-reported success is not enough to mark an effect realized.

## Record format

Append one JSON object per line to `docs/ops/help-wanted-realization-evidence.jsonl` only after a verifier independent of both the contributor and the operator has inspected the linked evidence.

```json
{
  "pr_url": "https://github.com/OWNER/REPO/pull/123",
  "status": "verified",
  "independence_attested": true,
  "verified_by": "independent-maintainer",
  "verified_at": "2026-10-18T10:00:00Z",
  "verification_method": "reproduced benchmark against released version",
  "evidence_summary": "The reported regression is absent in the published release.",
  "effect_url": "https://github.com/OWNER/REPO/releases/tag/v1.2.3",
  "verification_url": "https://github.com/OWNER/REPO/actions/runs/123"
}
```

## Validation rules

- `pr_url` must exactly match the canonical upstream PR URL in the audit ledger.
- `status` must be `verified`; `independence_attested` must be boolean `true`.
- `verified_by` must be present and must not be the PR contributor, the configured operator identity, or `github-actions[bot]`.
- `verified_at` must be an ISO-8601 timestamp with an explicit UTC offset or `Z` (for example `2026-10-18T10:00:00Z`); timestamps without a timezone are rejected.
- `verification_method` and `evidence_summary` must be non-empty.
- `effect_url` and `verification_url` must be HTTPS links to the observed effect and its verification evidence.
- Invalid records are ignored as proof and appear as an evidence gap. Do not invent records to improve metrics.

The automated validator enforces the shape and identity-separation rules; it cannot establish the truth of an attestation merely from the JSON. The linked evidence and verifier's independence remain subject to human review. Never place credentials, private payloads, prompts, or completions in this registry.

## Coverage accumulation

The hourly audit refresh remains bounded to 25 upstream PRs per run. The generated audit file now retains the latest audit result for every currently known PR across runs, so coverage accumulates instead of resetting to the current sample. It reports `audited_pr_count` (historical coverage with a successful observation), `audited_this_run_count` (successfully observed PRs in the current batch), `attempted_this_run_count` (all attempts, including failed/deferred ones), and `not_audited_count` (PRs with no complete observation anywhere in retained history). A later partial attempt remains visible as the current status but does not erase the timestamp/SHA of the last complete observation; this keeps historical coverage monotonic while current-batch completeness remains explicit. Deferred or unavailable attempts do not erase prior known stages; the last attempt status and evidence gaps are retained separately. A PR's cached stage is last-observed evidence, not a guarantee that its upstream state has not changed since that observation.
