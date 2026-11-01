# Platform Objects

One job: describe the bounded Android execution surface and its trusted control boundary.

## Inputs

- Object index: [`../_index.md`](../_index.md)
- Stale architecture context: [`termux-agentic-hub.md`](termux-agentic-hub.md), with the archived source linked from that card
- Governance: [`../governance/change-control.md`](../governance/change-control.md)
- Fleet App identities: [`github-app-fleet.md`](github-app-fleet.md), with the AppID process records it cites

## Process

1. Read the Termux Agentic Hub card and the BLU B160V and Free-Services Envelope card when device or service assumptions are relevant. For fleet GitHub-App identity work (AppIDs, actor permissions, telemetry), read the GitHub App Fleet card and its AppID-process sources instead — that surface is repository-side, not device-side.
2. Confirm whether the requested operation is **Observe**, **Operate**, **Change**, or **Critical**.
3. Treat the device/free-services envelope as a design constraint, not proof of current availability.
4. Re-verify a current canonical architecture source before any execution work; do not assume an interactive device shell, live hub, or MCP transport is available.

## Outputs

- A bounded change scope or an explicit statement that the request needs human approval or is outside the supported path.

## Human check

Verify the proposed operation preserves the policy boundary, stays within the declared device/service envelope, and does not expose credentials, interactive MFA, or a public shell.
