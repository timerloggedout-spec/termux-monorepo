# Multi-project inference identity — design

**Status:** approved implementation scope from the operator directive, 2026-11-19.

## Intent

Define a provider-neutral identity contract for inference work executed concurrently across multiple projects. Attribute each observation to a portfolio, project, task, logical inference, and individual attempt so project isolation and portfolio-level utilization can coexist.

## Goals

- Extend the existing Integration Intelligence event envelope additively.
- Give project profiles stable, paired `portfolio_id` and `project_id` identifiers when they opt into inference attribution.
- Give inference events stable task, inference, and attempt identities.
- Represent project queues and shared concurrency groups as attribution metadata.
- Preserve provider/model/configured-instance identity, usage provenance, unknown values, and legacy event compatibility.
- Map completed attempts into the existing `3l0-intake/v1` contract.

## Non-goals

- Implement a runtime scheduler, queue service, concurrency limiter, provider router, retry engine, or budget controller.
- Create a second event ledger, project registry, or 3L0 scoring system.
- Implement Codex OTel, ChatGPT Desktop, Termux, or GitHub provider adapters.
- Capture prompts, completions, raw tool payloads, secrets, or private session transcripts.

## Approaches

1. **Extend Integration Intelligence and Project Profile contracts — selected.** Reuses the repository's canonical event envelope, project profile schema, provenance rules, and 3L0 intake mapping. This keeps one event boundary and preserves existing records through optional fields and event-type conditionals.
2. **Create a separate inference ledger and schema.** Gives inference events a dedicated file, but duplicates event identity, provenance, validation, and ingestion semantics already owned by Integration Intelligence.
3. **Build a scheduler and telemetry stack together.** Adds immediate runtime behavior, but exceeds the requested first vertical slice and risks duplicating existing routing, quota, and scoring ownership.

## Architecture

Use `(portfolio_id, project_id)` as the owning scope. A task belongs to one project. A logical `inference_id` may have multiple execution attempts; every attempt receives a unique `attempt_id`. Each event retains its own `event_id` and idempotency key.

Project queues use `queue_id`; portfolio-level shared capacity uses `concurrency_group_id`; scheduling priority uses `priority_class`. These are descriptive contract fields for future orchestration. Existing routing and quota owners retain execution authority.

The event schema adds optional `project`, `task`, and `inference` objects. `inference.*` events require those objects. Project profiles accept `project_id` and `portfolio_id` as an optional pair. Every inference event carries a usage object; usage values remain nullable and carry explicit measurement and attribution states.

Completed attempts map to `3l0-intake/v1` using the attempt as dispatch identity and the existing provider, model, endpoint, instance, run, usage, and outcome fields. 3L0's confirmed/corroborated scoring rules remain authoritative.

## Constraints and acceptance

- Keep existing `integration-event.schema.json` required fields and `schema_version` unchanged.
- Validate legacy event examples unchanged.
- Validate inference events with complete project/task/inference identity.
- Reject missing project/task/inference identity, missing attempt identity, negative usage, and activity-only numeric measurements.
- Validate project profiles with both stable IDs and reject profiles declaring only one.
- Preserve configured instance identity and explicit null semantics.
- Keep raw prompts, completions, tool payloads, credentials, and transcripts outside the event record.
- Run the focused tests, proposal validator, repository gate, and Termux smoke on one immutable PR head.
