# TLM — Telemetry & Learning Matrix run receipt

**Contract version:** 1.0  
**Purpose:** minimal, structured, redacted record for comparable trials  
**Rule:** observed data and reviewer interpretation must remain separate.

## Required fields

| Field | Requirement |
|---|---|
| `receipt_schema` | Contract version, e.g. `tlm-run-receipt/v1` |
| `trial_id`, `candidate_id`, `candidate_version` | Stable IDs; never rely on a mutable branch name alone |
| `source` | Commit SHA plus path/blob SHA for instructions/config under test |
| `environment` | Platform/device class, OS/runtime/CLI versions, relevant capability flags |
| `scenario_id`, `fixture_ids` | Same scenario and fixture IDs across comparable candidates |
| `authorization` | Authorized actor/scope reference, target class, allowed action category; do not copy credentials |
| `started_at`, `ended_at` | UTC timestamps with timezone |
| `action_category` | Short category or command template; redact private args, prompts, paths and tokens |
| `result`, `process_exit_code` | Separate semantic result from actual process exit |
| `duration_ms` | Measured elapsed time, or null if unavailable |
| `resources` | CPU/memory/disk/network/quota observations only when available; unknown stays null |
| `assertions` | Expected result, observed result, pass/fail/unknown and test reference |
| `retries`, `timeouts` | Explicit numeric counts and timeout state |
| `state_changes` | Before/after hashes or redacted diff refs where relevant |
| `recovery` | Not-needed / succeeded / failed / unknown, with evidence ref |
| `evidence` | Stable links or artifact identifiers, plus integrity hashes when available |
| `limitations` | Missing data, platform gaps, confounders, historical vs current labels |
| `review` | Reviewer ID/role, confidence, objection, review timestamp; never infer consensus |

Do not record secrets, credentials, host private keys, private raw prompts/completions, unrelated workspace contents, or personal data. If raw artifacts are essential, keep them access-controlled and refer to them by opaque ID and hash. Do not create a duplicate telemetry pipeline if an existing receipt already satisfies this contract; map its fields and document gaps.

## Minimal JSON example

This is a **schema illustration only**, not a real execution receipt. Null values mean unknown, not zero or pass.

```json
{
  "receipt_schema": "tlm-run-receipt/v1",
  "trial_id": "MVT-EXAMPLE-001",
  "candidate_id": "V0",
  "candidate_version": "as-found",
  "source": {
    "commit_sha": "REPLACE_WITH_IMMUTABLE_SHA",
    "files": [
      {
        "path": "REPLACE_WITH_PATH",
        "blob_sha": "REPLACE_WITH_BLOB_SHA"
      }
    ]
  },
  "environment": {
    "platform": "REPLACE_WITH_PLATFORM",
    "os_version": null,
    "runtime_versions": {},
    "capabilities": {}
  },
  "scenario_id": "SCENARIO-001",
  "fixture_ids": [],
  "authorization": {
    "scope_reference": "REPLACE_WITH_APPROVAL_OR_EXISTING_SCOPE_REFERENCE",
    "target_class": "REPLACE_WITH_TARGET",
    "allowed_action_categories": []
  },
  "started_at": null,
  "ended_at": null,
  "action_category": "REDACTED_ACTION_TEMPLATE",
  "result": "unknown",
  "process_exit_code": null,
  "duration_ms": null,
  "resources": {
    "quota": null,
    "cpu": null,
    "memory_bytes": null,
    "disk_bytes": null
  },
  "assertions": [
    {
      "id": "ASSERT-001",
      "expected": "REPLACE_WITH_EXPECTATION",
      "observed": null,
      "status": "unknown",
      "evidence_ref": null
    }
  ],
  "retries": 0,
  "timeouts": 0,
  "state_changes": [],
  "recovery": {
    "status": "unknown",
    "evidence_ref": null
  },
  "evidence": [],
  "limitations": [
    "Illustration only; no trial was executed."
  ],
  "review": {
    "reviewer_role": null,
    "confidence": "low",
    "objection": null,
    "reviewed_at": null
  }
}
```

## Integrity and comparability rules

- Store receipts as immutable per-run artifacts; corrections create a new receipt revision with a link to the original.
- Use UTC timestamps, explicit units, stable IDs, and commit/blob hashes.
- Record actual process exit independently from a CLI-reported status.
- Never sum cumulative usage snapshots unless the source contract says they are deltas.
- Keep raw data separate from normalized metadata and interpretation.
- Mark missing fields unknown; do not impute, interpolate or convert unavailable metrics into zero.
- Compare only matching scenarios, fixtures, platform assumptions and budgets. Label non-matching comparisons inconclusive.
- Keep test results, model/reviewer opinions and operator decisions as separate evidence types.
