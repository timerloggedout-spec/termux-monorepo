---
type: process
universe: live
status: verified
consumes:
  - ../objects/platform/termux-agentic-hub.md
  - ../objects/governance/change-control.md
produces:
  - redacted result envelope
  - repository audit evidence
verified_at: 2026-08-17
---

# Structured Termux Job

A permitted Android operation moves from a reviewed GitHub request through schema and capability validation to one bounded local device action and a redacted, auditable result.

## Input → Movement → Output

The input is a valid structured job with identity, capability, arguments, and approval data. `hub_mcp` validates the job and dispatches one named capability to the local Termux worker; the output is a bounded, redacted result envelope that can be reviewed as repository evidence.

## Why this shape

Allowing repository events or agents to provide an arbitrary shell string would bypass capability checks, widen the attack surface, and erase the intended audit boundary.

## Steps

1. Confirm the request maps to a named capability and the appropriate approval tier. Cite `docs/architecture/termux-agentic-hub.md:41-50`.
2. Validate the structured job, including timestamps, fields, privileges, and replay protection. Cite `docs/architecture/termux-agentic-hub.md:52-56`.
3. Execute the named capability through the single local worker and canonical Termux MCP/Termux:API route. Cite `docs/architecture/termux-agentic-hub.md:9-25`.
4. Return a bounded, redacted result envelope for review. Cite `docs/architecture/termux-agentic-hub.md:25-28`, `docs/architecture/termux-agentic-hub.md:54-56`.
5. Reject interactive MFA, OTP capture, public SSH publication, and unsupported Android GitHub Actions runner behavior. Cite `docs/architecture/termux-agentic-hub.md:62-64`.

## If you change this

- **Hits:** capability definitions, validation, replay protection, redaction, adapter policy, and device-bound smoke/policy checks.
- **Does not hit:** generic repository editing or a developer’s local shell workflow.

## Surfaces

| Surface | Role |
|---|---|
| GitHub review/CI | Provides the controlled request and receives audit evidence. |
| `hub_mcp` | Validates the structured job and enforces policy. |
| Termux worker | Executes one bounded local capability. |
| Human operator | Supplies required approval and handles excluded interactive edges. |

## See

- Objects: [`../objects/platform/termux-agentic-hub.md`](../objects/platform/termux-agentic-hub.md)
- Source: [`docs/architecture/termux-agentic-hub.md`](../../architecture/termux-agentic-hub.md)
