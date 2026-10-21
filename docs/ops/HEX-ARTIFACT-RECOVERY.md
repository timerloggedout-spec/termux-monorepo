# Hex Artifact Recovery & Relevance Register

**Status:** active forensic register  
**Tracking issue:** #522  
**Canonical Hex contract:** `3l0.moneyball.v1`

## Why this exists

A ZIP observed in an agent sandbox may be:

1. a GitHub Actions artifact ZIP;
2. a Hex-native export/package;
3. an unrelated agent/session archive.

The repository currently proves the first mechanism exists. It does **not** prove that a historical native Hex ZIP was received, checked in, or imported.

Do not classify a recovered ZIP by filename alone.

## Provenance tiers

| Tier | Evidence | Meaning |
| --- | --- | --- |
| A | Exact bytes + SHA-256 + source run/attempt + artifact metadata | Strong provenance; safe to analyze |
| B | Exact bytes + SHA-256 + known originating session/path, but no GitHub run | Useful forensic artifact; provenance incomplete |
| C | Filename/description only | Candidate lead; not evidence |
| D | Memory/claim without bytes | Hypothesis only |

## Known repository artifact lane

`.github/workflows/hex-moneyball-evidence.yml` sanitizes an NDJSON event stream and publishes a GitHub Actions artifact with:

- `evidence.ndjson`
- `evidence.csv`
- `receipt.json`

The artifact name is `hex-moneyball-evidence-{run_id}-{run_attempt}` and the workflow currently retains it for 14 days.

This is **Hex-compatible evidence transport**, not proof of a native Hex export.

## Canonical Hex-side contract

`docs/ops/HEX-MONEYBALL-INTEGRATION.md` defines:

- five datasets: `experiment_run`, `agent_task_attempt`, `provider_call`, `outcome_score`, `manager_decision`;
- stable run/attempt/call/score/decision identities;
- contract `3l0.moneyball.v1`;
- metadata-first privacy boundary;
- raw pass rate, confidence-weighted score, and cost-per-success metrics;
- validation, reconciliation, freshness, idempotency, contract-drift, calculation-drift, and matcher-quality gates;
- the intended Hex project topology and refresh policy.

## Observed Hex connector capability boundary

The connected Hex integration exposes project search plus analysis-thread create/get/continue operations. A project search was attempted during this investigation and the platform returned: **MCP server access requires a Team or Enterprise plan**.

Therefore:

- the connector surface is known;
- live project contents were **not** inspected;
- no Hex thread/project/ZIP provenance was established by that attempt;
- invoking the connector must not be recorded as successful workspace access.

See `docs/ops/HEX-CAPABILITY-REGISTER.md` for the complete capability/access record.

## SHE relationship

The SHE dashboard must treat Hex as an optional analytical consumer. GitHub commits/PRs/issues/reviews/checks/Actions and the durable historical corpus remain authoritative.

A recovered ZIP is relevant to SHE only if it can be mapped to:

`artifact -> source run/attempt -> source SHA -> corpus snapshot -> contract/schema -> derived metric`

Otherwise it may be useful research material, but it must remain marked `UNVERIFIED`.

## Recovery record

When a candidate ZIP is found, record:

```text
artifact_id:
filename:
sha256:
byte_size:
origin_kind: github-actions | hex | agent-sandbox | unknown
origin_run_id:
origin_run_attempt:
origin_session:
origin_path:
observed_at:
created_at:
contract_version:
schema_versions:
source_sha:
source_ref:
corpus_snapshot_id:
coverage_state:
contents:
provenance_tier:
relevance:
notes:
```

`relevance` should be one of `direct`, `supporting`, `historical-lead`, `unrelated`, or `unknown`.

## Current finding

No repository evidence currently identifies a historical native Hex ZIP. The SHE PRD therefore correctly says the ZIP is **not established / not incorporated**.

The next forensic targets are:

1. retained GitHub Actions artifact inventory;
2. agent/session sandboxes that may contain a candidate ZIP;
3. repository receipts/manifests that preserve expired-artifact provenance;
4. any future Hex export with exact bytes and contract/schema metadata.

If the 14-day GitHub artifact retention has expired, the repository receipt/manifest and session provenance become the reconstruction anchors.

## Related artifacts

- `docs/ops/SHE-DASHBOARD-PRD.md`
- `docs/ops/SHE-DASHBOARD-INDEX.md`
- `docs/ops/SHE-DASHBOARD-ARCHITECTURE.mmd`
- `docs/ops/SHE-DASHBOARD-SNAPSHOT-CONTRACT.md`
- `docs/ops/HEX-CAPABILITY-REGISTER.md`
- `docs/ops/HEX-MONEYBALL-INTEGRATION.md`
- `scripts/hex_moneyball_export.py`
- `tests/test_hex_moneyball_export.py`
- `.github/workflows/hex-moneyball-evidence.yml`
- `workspace/llm_map/context_relationships/manifest.json`
- `workspace/llm_map/context_relationships/build-summary.json`
