# Platform Objects

One job: describe the bounded Android execution surface and its trusted control boundary.

## Inputs

- Object index: [`../_index.md`](../_index.md)
- Architecture source: [`../../../architecture/termux-agentic-hub.md`](../../../architecture/termux-agentic-hub.md)
- Governance: [`../governance/change-control.md`](../governance/change-control.md)

## Process

1. Read the Termux Agentic Hub card.
2. Confirm whether the requested operation is **Observe**, **Operate**, **Change**, or **Critical**.
3. Follow the cited architecture and governance source; do not assume an interactive device shell is available.

## Outputs

- A bounded change scope or an explicit statement that the request needs human approval or is outside the supported path.

## Human check

Verify the proposed operation preserves the policy boundary and does not expose credentials, interactive MFA, or a public shell.
