# Foresight Evidence Spine

## Purpose

Provide one portable evidence/provenance interchange layer for the monorepo's:

- daily research digest;
- Foresight Radar (H0/H1/H2/H3);
- FOSS procurement matrix;
- agent observability/evaluation;
- reproducibility and environment experiments;
- historical evidence and decision records.

The spine is deliberately **not** a replacement for SQLite, OpenTelemetry, GitHub Actions, Langfuse, Phoenix, or other adapters. It is the stable, inspectable record exchanged between them.

## Architecture

```
Primary sources / papers / releases / advisories
                  |
                  v
          retrieval/research agents
                  |
                  v
       resource-registry.jsonl
          |       |       |
          |       |       +--> procurement export
          |       +----------> Foresight Radar
          +------------------> daily digest
                  |
                  v
      telemetry / mapper / evaluation adapters
```

## Evidence semantics

| Horizon | Meaning |
|---|---|
| H0 | confirmed |
| H1 | emerging |
| H2 | weak signal |
| H3 | speculative |

Horizon and evidence status are separate. A source can be authoritative while a claim remains an attributed claim or early signal.

Evidence status values:

- `confirmed`
- `research_finding`
- `attributed_claim`
- `early_signal`
- `speculative`

## Procurement matrix

Each resource may carry:

license, canonical source, maintenance, portability, offline capability,
interoperability, reproducibility, provenance, dependency risk, lock-in risk,
security surface, resource cost, operational fit, horizon, confidence, and
decision status.

Decision status is descriptive state, not a universal ranking:

- `watch`
- `investigate`
- `prototype`
- `adopt`
- `reject`
- `defer`

## Integrity model

Records are append-oriented JSONL. Corrections append a newer record using the
same `resource_id`; consumers deduplicate to the latest record.

Each normalized record receives a SHA-256 `evidence_hash` over canonical JSON
with the hash field excluded. This detects accidental mutation without requiring
a hosted service.

## Portability

The implementation is Python standard-library only and is intended to run on:

- Termux/Android;
- Linux;
- CI runners;
- Docker;
- Codespaces.

No network access is required by the registry itself. Retrieval remains an
upstream concern.

## Security

Never store secrets, cookies, API tokens, browser profiles, or credentials in
the registry. Reference protected artifacts by hash or controlled identifier.

## Operational rule

`QUEUED`, `IN_PROGRESS`, and `COMPLETED` are runtime states, not evidence
of correctness. Evidence records should link to the execution/run/attempt and
preserve source SHA, timestamps, artifact identifiers, and validation status
when available.
