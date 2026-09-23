---
name: plugin-connector-parity
description: Review and document parity between the currently exposed ChatGPT/plugin/MCP connector surface and repository-native integrations. Use before integrating new external tooling, when connector capabilities change, or when auditing collaborator/admin parity.
---

# Plugin Connector Parity

## Purpose

Keep a reproducible, evidence-backed boundary between:

`EXPOSED → CONNECTED → AUTHORIZED → OBSERVED → ADAPTED → INTEGRATED → VALIDATED`

Never treat connector exposure as proof of authentication, authorization, runtime success, or repository integration.

## Review sequence

1. **Observe** the current tool/provider surface.
2. **Inventory** provider names, action counts, and major read/write capacities.
3. **Compare** the live surface against `docs/ops/PLUGIN-CONNECTOR-CAPABILITY-MATRIX.md` and `.github/connectors/integrations.yaml`.
4. **Classify** each delta as additive, changed, removed, duplicate, or security-sensitive.
5. **Choose** only bounded, high-leverage integrations with a concrete repository use case.
6. **Act** through the smallest repository change: registry, adapter, skill, test, or workflow.
7. **Verify** with deterministic checks and a live provider call where authorized.
8. **Record** evidence, timestamp, state transition, and remaining gaps.
9. **Repeat** only while the new evidence changes the decision.

## Evidence rules

- Keep verified facts separate from candidate relationships.
- Cite repository sources for existing integration contracts.
- Record provider/tool availability separately from authentication.
- Never store secrets, tokens, session bodies, browser profiles, or private provider payloads.
- Do not infer provider availability from historical artifacts or names.
- Do not add a second abstraction when an existing first-party/native capability already owns the boundary.
- Prefer adapters with clear ownership, idempotence, bounded scope, and reversible promotion.

## Parity contract

A provider is **repo-integrated** only when all applicable evidence exists:

- named repository owner/adapter;
- documented purpose;
- input/output contract;
- permission boundary;
- deterministic test or fixture;
- runtime observation/evidence path;
- failure/rollback behavior;
- entry in the repository connector registry;
- collaborator-facing documentation/skill when humans or agents must invoke it.

## Safety

Use read-only review unless an explicit apply request exists. Do not merge, rotate/revoke credentials, delete data, force-push, or send external messages as part of parity discovery.

## Closeout

Report:

- current snapshot;
- providers added/removed/changed;
- repository parity gaps;
- integrations actually validated;
- tests/evidence;
- next bounded actions.

