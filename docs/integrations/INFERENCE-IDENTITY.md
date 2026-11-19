# Multi-project inference identity

Status: **contract defined; provider adapters and scheduling remain follow-on work**.

## Purpose

Give every inference observation a stable project, task, logical inference, and execution-attempt identity. Support concurrent work across projects while retaining one portfolio-level view and the existing Integration Intelligence event envelope.

## Identity hierarchy

`portfolio_id + project_id` identifies the owning project scope. `task_id` identifies work within that scope. `inference_id` identifies one logical inference request. `attempt_id` identifies one provider execution attempt.

```text
portfolio_id
  └── project_id
       └── task_id
            └── inference_id
                 ├── attempt_id
                 ├── provider / model / endpoint_id
                 ├── instance_key
                 ├── session_id / run_id
                 └── outcome + usage evidence
```

- Keep `project_id` stable and unique within its portfolio.
- Keep task and inference lineage within the owning project.
- Reuse `inference_id` across retries; issue a new `attempt_id` for each provider execution.
- Increment `attempt_number` for each retry when the source reports the sequence.
- Keep `event_id` and `idempotency_key` unique per captured event.
- Preserve `model: null` and null usage values when the source leaves them unknown.
- Preserve the configured `instance_key`; provider/model labels alone do not identify a configured instance.

## Parallel execution dimensions

- `queue_id` separates project queues.
- `concurrency_group_id` identifies shared portfolio capacity or a declared concurrency pool.
- `priority_class` supports critical, normal, background, and experiment work.
- Project isolation remains the default ownership boundary. Cross-project work requires an explicitly authorized handoff and a separately attributable target-project task.

These fields describe execution and attribution. The contract does not implement a scheduler, queue service, quota enforcer, provider router, or budget controller.

## Event contract

The existing `integration-event.schema.json` remains the shared event envelope. The `integration_id` must match a canonical registry entry; `codex-otel` and `chatgpt-desktop` are registered as discovered sources with planned repository adapters. The extension adds optional `project`, `task`, and `inference` objects. Events whose `event_type` begins with `inference.` require all three objects and require stable `inference_id`, `attempt_id`, and provider identity.

Every inference event carries a usage object. Usage fields include input, cached-input, output tokens, credits, estimated cost, currency, measurement status, and attribution; source-unknown values remain null. Use `measured`, `estimated`, `activity_only`, or `not_established` as the measurement status. For activity-only and not-established observations, every numeric usage value and currency remain null. Preserve estimates as estimates and provider-reported measurements as provider-reported.

## Project profiles

`ops/projects/profile.schema.json` accepts optional `project_id` and `portfolio_id` fields. Profiles that declare either field provide both. Existing profiles remain valid without either field; inference events require both identifiers in their project context.

## 3L0 linkage

Map completed inference attempts into the existing `3l0-intake/v1` record at the routing/dispatch boundary:

| Inference event | 3L0 intake |
|---|---|
| `attempt_id` | `dispatch_id` |
| `provider`, `model`, `endpoint_id` | `provider`, `model`, `endpoint` |
| `instance_key` | `instance.instance_key` |
| `session_id`, `run_id` | `run.session_id`, `run.run_id` |
| measured input/output tokens | `usage.tokens_in`, `usage.tokens_out` |
| observed execution duration | `usage.latency_ms` |
| explicit attempt/retry evidence | `usage.retries` |

Populate only fields supported by source evidence. Carry unknown values as null or the 3L0 plane's `NOT ESTABLISHED` representation. 3L0 scoring continues to require confirmed and corroborated outcomes under its existing fold rules; inference volume and tool activity remain observational evidence by default.

## Privacy and provenance

- Store IDs, metadata, counts, statuses, hashes, and opaque evidence references.
- Keep prompts, completions, raw tool arguments/results, credentials, and private session transcripts in their approved source systems.
- Record provider, capture method, model, adapter version, and attribution class through the existing provenance envelope.
- Treat provider observations as evidence inputs, not repository authority.

## Compatibility

The event schema remains version `1.0.0` because the extension is additive and optional for existing event types. Legacy integration events continue to validate unchanged. The inference event conditional makes the identity tuple mandatory only for `inference.*` event types.
