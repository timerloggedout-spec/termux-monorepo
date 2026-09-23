---
name: plugin-connector-parity
description: Production-side parity review for external connector capability, repository integration, and evidence state.
---

# Plugin Connector Parity — CI / Production

Treat connector state as an evidence state machine:

`EXPOSED → CONNECTED → AUTHORIZED → OBSERVED → ADAPTED → INTEGRATED → VALIDATED`

## Production gate

A connector integration must not be promoted solely because:

- a provider is listed;
- a tool is exposed;
- a configuration file exists;
- a workflow is queued;
- a dashboard is green without runtime evidence.

Promotion requires the repository contract, deterministic validation, and runtime evidence appropriate to the integration.

## Required checks

- registry/schema validity;
- no secret material in source, artifacts, or logs;
- explicit ownership and permission boundary;
- idempotent/retry-safe behavior where external writes exist;
- bounded artifact/evidence contract;
- failure classification that distinguishes provider, network, orchestration, code, and environment failures;
- collaborator parity: the documented skill and registry agree.

## Review loop

`RECON → PLAN/MEASURE → ACT → COMMIT → WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → CLASSIFY → RECORD → REPEAT`

Queued/in-progress is not success. Failed executions remain observations unless a separate rerun is explicitly justified.

## Canonical artifacts

- `docs/ops/PLUGIN-CONNECTOR-CAPABILITY-MATRIX.md`
- `.github/connectors/integrations.yaml`
- `.agents/skills/plugin-connector-parity/SKILL.md`
- this file

