# Agent Harness Admission Contract

## Purpose

Treat agent skills, hooks, MCP servers, subagents, workflow extensions, and agent configuration as dependency classes.

This contract is intentionally admission-oriented and read-only at first. It does not silently grant execution authority and does not replace the repository's existing review/gate system.

## Required identity

Every admitted component should have:

- immutable source URL;
- version, tag, or commit;
- SHA-256 content hash;
- observed-at timestamp;
- evidence status;
- source commit when applicable.

## Requested authority

Record requested permissions separately for filesystem paths, network destinations, process/subprocess capabilities, and named secret scopes.

A component that has not declared its requested authority is **UNVALIDATED**, not zero-risk.

## Admission states

- UNVALIDATED: observed but not yet checked.
- ADMITTED: passes the repository policy for the intended cohort.
- REJECTED: violates an explicit policy.
- HOLD: blocked by missing evidence or unresolved risk.

These states are not model-quality scores.

## Security evidence

The *Scanning the Harness* study examined 3,171 public repositories and found validated defect classes involving unpinned MCP servers and pre-approved execution/shell permissions. Its rates remain research findings, not ecosystem-wide probabilities.

Primary source: https://arxiv.org/abs/2609.07360

## Implementation rule

The next scanner should be read-only and produce:

1. detected component;
2. source/version/hash;
3. requested permissions;
4. policy rule IDs;
5. admission status;
6. unresolved questions;
7. evidence receipt.

It must not install components, execute discovered commands, weaken policy, or mutate credentials.

## Telemetry relationship

OpenTelemetry GenAI/MCP conventions remain an adapter input while upstream conventions are Development status. Canonical evidence remains the repository-owned closed JSONL contract.

## MCP relationship

MCP 2026-07-28 is the protocol baseline. Protocol-level statelessness does not remove application-level state; application state should be explicit and auditable.

## Promotion

Admission evidence is additive to:

`REVIEW → CHECKS → ACTION→EFFECT → ATES/WTCV → LONGITUDINAL RECORD`

No speed-only or model-score-only admission gate is permitted.
