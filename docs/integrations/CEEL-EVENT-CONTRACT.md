# CEEL event awareness and GitHub-native execution contract

## Principle

Awareness is event-driven. The system responds to changes when they happen and reconciles gaps when necessary. Weekly summaries may support human review, but they are not the sensing or dispatch mechanism.

## Event sources and handlers

| Event | Identity | Existing handler/path | Required output |
|---|---|---|---|
| push | repository + before/after SHA + ref | GitHub Actions path filters and CI | changed capability paths and pinned after-SHA |
| pull_request | PR number + head/base SHA + action | existing PR validation and recon-intel | candidate delta, tests and review linkage |
| release | tag + target commit + release ID | bounded release workflow | source version event and comparison trigger |
| issues | issue number + action + labels | Delphi intake / proposal lifecycle | proposal/capability linkage |
| issue_comment | issue + comment ID + actor + command/form | existing command and Delphi routes | validated request; never arbitrary shell |
| workflow_run | workflow ID + run ID + head SHA + conclusion | evidence reconciliation | intended effect vs execution result |
| repository_dispatch | allowlisted event type + client payload ID | existing receiver mesh / bounded dispatch | normalized integration event |
| provider webhook | provider event ID + delivery ID + signature + source version | future separately gated receiver | verified, redacted, idempotent event |

## Admission and processing

1. Verify event type is allowlisted for the integration.
2. Verify webhook signature where applicable; reject unverifiable write-triggering events.
3. Validate payload size, schema, timestamp window, source identity, repository allowlist and immutable revision.
4. Derive idempotency key from provider delivery/event identity and source version, not arrival time alone.
5. Redact secret-shaped fields and raw prompt/completion content before artifacts or logs.
6. Append normalized event reference through existing Integration Intelligence evidence path.
7. Classify as discovery, proposal, experiment, validation or reconciliation.
8. Dispatch only the least-privilege existing workflow that owns the action.
9. Record queue/admission, execution, effect, validation and promotion separately.
10. Re-fetch source state before acting on stale or reordered events.

## Delivery semantics

Assume at-least-once delivery. Deduplicate by idempotency key; duplicates do not create duplicate observations. Preserve out-of-order arrivals with event time, capture time and source version. Missing delivery is not evidence of no change. Retry transient errors with bounded exponential backoff and provider Retry-After support. Stop on authentication, signature, permission, schema, privacy or source-integrity errors. Persist cursors only after durable acknowledgement. Reconciliation emits findings; it does not rewrite prior evidence.

## Cadence and fallback

Primary: GitHub events, provider webhooks and event-driven workflow completion.

Fallback: existing bounded reconciliation workflows, cursor-based incremental reads for sources without webhooks, and operator-triggered health probes. Reconciliation frequency follows source rate limits, freshness requirements and measured missed-event risk—not a blanket weekly cadence. Scheduled fallback is bounded, read-only and observable.

## Authority and permissions

Default contents: read; no generic write token. Issue/PR writes belong to existing proposal/Delphi workflows. Workflow-file writes remain subject to the explicit Workflows permission boundary. Provider writes, paid calls, data exports, deployments and model routing changes require separately authorized work. External event content is untrusted, never agent or shell instructions. Workflow success is execution evidence, not proof of desired outcome.
