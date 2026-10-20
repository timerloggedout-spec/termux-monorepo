# Foresight Evidence Spine

## Purpose

Provide one portable evidence/provenance interchange layer for the monorepo's daily research digest, Foresight Radar, FOSS procurement matrix, agent observability/evaluation, reproducibility experiments, and historical evidence.

The spine is deliberately **not** a replacement for SQLite, OpenTelemetry, GitHub Actions, Langfuse, Phoenix, or other adapters. It is the stable, inspectable record exchanged between them.

## Contract v2

Every normalized evidence record has three stable identities:

- `resource_id`: durable identity for the source/resource being tracked.
- `item_id`: durable identity for a briefing/radar item derived from that resource.
- `lane_id`: stable research lane that owns the interpretation.

For compatibility, normalization derives `item_id` from `resource_id` and `lane_id` from `category` when older records omit them. New producers should write them explicitly.

`canonical_source` is a top-level copy of `source.url`; validation rejects divergence so exports and downstream systems have one canonical source field.

## Evidence semantics

| Horizon | Meaning |
|---|---|
| H0 | confirmed / material |
| H1 | emerging / credible |
| H2 | weak signal |
| H3 | speculative |

Horizon and evidence status are separate. A source can be authoritative while a claim remains an attributed claim, early signal, or disputed finding.

Evidence status values:

- `confirmed`
- `research_finding`
- `attributed_claim`
- `early_signal`
- `speculative`
- `disputed`

## Procurement

The procurement object carries license, canonical source, maintenance, portability, offline capability, interoperability, reproducibility, provenance, dependency risk, lock-in risk, security surface, resource cost, operational fit, horizon, confidence, and decision status.

Decision status is descriptive state, not a universal ranking: `watch`, `investigate`, `prototype`, `adopt`, `reject`, `defer`.

## Integrity

Records are append-oriented JSONL. Corrections append a newer record with the same `resource_id`; consumers deduplicate to the latest record.

Each normalized record receives a SHA-256 `evidence_hash` over canonical JSON with the hash field excluded. No hosted service is required.

## Radar query

The portable CLI exposes:

`python -m foresight.registry --registry data/foresight/resource-registry.jsonl radar --horizon H1 --lane agent-observability`

This keeps radar extraction deterministic and machine-readable without requiring a dashboard or vendor service.

## Operational validation

CI executes the unit suite and validates the committed registry corpus. An empty-registry initialization smoke-test is not sufficient evidence that the contract is exercised.

## Portability and security

Python standard-library only; intended for Termux/Android, Linux, CI, Docker, and Codespaces. The registry requires no network access.

Never store secrets, cookies, API tokens, browser profiles, or credentials in evidence records. Reference protected artifacts by hash or controlled identifier.
