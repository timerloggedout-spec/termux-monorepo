# Provider Observation Log

> **Current state: no observations recorded.** Provider polling has not been configured or run from this ICM workspace.

## Record format

Append an entry only after the provider source, cadence, credentials model, retention rule, and human reviewer have been approved in writing. Each entry must be redacted, attributable, and non-executable.

| Field | Required content |
|---|---|
| Observation ID | Stable local identifier. |
| Recorded at | UTC timestamp. |
| Provider record | One record from [`registry.md`](registry.md). |
| Source | Approved URL, API operation, or repository source path. |
| Trigger and cadence | Manual, scheduled, or event-triggered, plus approved frequency. |
| Redacted finding | Minimal factual observation; never include a secret or full request/response payload. |
| Status | `candidate`, `accepted`, or `rejected`. |
| Reviewer | Human who accepted or rejected the record. |
| Runtime effect | Always `none` for this documentation record; link a separate code/workflow proposal for any future execution change. |

## Rejection rule

If an observation cannot be safely redacted, cannot identify its source, or would be used to alter runtime routing without a separate approved code/workflow change, do not record it here. Open or link a governance item instead.
