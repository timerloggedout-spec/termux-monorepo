---
type: process
universe: ghost
status: stale
consumes:
  - ../objects/platform/termux-agentic-hub.md
  - ../objects/governance/change-control.md
produces:
  - future recovery proposal or explicit non-execution finding
verified_at: 2026-08-17
---

# Structured Termux Job

This is an archived process model for moving a permitted Android operation through reviewed schema and capability validation to one bounded local device action and a redacted result envelope. Its original architecture source is not present on current `master`; the process is retained only to preserve the intended safety shape for later recovery review.

## Current rule

Do **not** execute this process. It does not authorize a Termux MCP call, device probe, local worker launch, capability invocation, credential operation, or interactive shell. The BLU B160V/free-services envelope remains a stale design constraint, not evidence that an execution path exists.

## Historical movement

The archived model expected a reviewed request to map to a named capability, pass validation and replay protection, execute through one bounded worker, and return a redacted audit envelope. This historical description remains useful for deciding whether a future, separately approved recovery proposal preserves the original policy boundary.

## Recovery gate

Before reviving any portion of this process:

1. Identify and approve a current canonical architecture source.
2. Re-verify device and service availability without assuming transport access.
3. Define capability schemas, approvals, redaction, failure behavior, and validation.
4. Obtain a separate code/workflow/device authorization; this ICM documentation does not supply one.

## First-order impact

**Hits:** future platform recovery, device-bound governance, capability policy, redaction, and audit design.
**Does not hit:** current provider routing, the initiated CCTV card surface, generic documentation work, or a live device operation.

## Evidence

[1] [`../objects/platform/termux-agentic-hub.md`](../objects/platform/termux-agentic-hub.md) preserves the stale architecture context and archive link.
[2] [`../_meta/master-rebuild-integration-evidence.md`](../_meta/master-rebuild-integration-evidence.md) defines the read-only preservation boundary for inherited material.
