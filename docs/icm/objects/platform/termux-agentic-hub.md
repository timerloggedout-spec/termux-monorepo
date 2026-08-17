---
type: object
cluster: platform
universe: live
status: verified
entity: docs/architecture/termux-agentic-hub.md
verified_at: 2026-08-17
---

# Termux Agentic Hub

The **Termux Agentic Hub** is the controlled bridge between GitHub-coordinated work and bounded operations on the Android device; it is not an unauthenticated remote shell.

## Why this shape

The architecture separates the repository coordination plane from the Android execution plane so authorized agents can perform useful device administration without accepting arbitrary shell text or exposing the phone publicly.

## Shape

- A controlled job moves from GitHub through `hub_mcp` validation to a single local Termux worker, then to named capability invocation and a redacted result envelope.
- `hub_mcp` is the policy, replay-prevention, validation, and result-redaction boundary; device adapters are declarative references, not execution policy.
- Capability levels distinguish observation and bounded maintenance from changes and critical actions.

Citations: `docs/architecture/termux-agentic-hub.md:3-6`, `docs/architecture/termux-agentic-hub.md:9-28`, `docs/architecture/termux-agentic-hub.md:32-50`, `docs/architecture/termux-agentic-hub.md:52-64`.

## Connected to

- **owns:** the documented policy boundary for device-bound work.
- **owned-by:** the monorepo’s architecture and governance documents.
- **joins:** GitHub review/CI coordination, structured job validation, local Termux execution, and audit results.
- **looks-like-but-is-not:** a generic interactive MCP or unrestricted SSH shell.

## If you change this

- **Hits:** `docs/architecture/termux-agentic-hub.md`, the declared adapter roles, structured job validation, redaction/audit behavior, and the relevant smoke or policy checks.
- **Does not hit:** generic root navigation and unrelated CLI subsystems merely because they share the repository.

## Surfaces

| Surface | Role |
|---|---|
| Authorized agent | Requests a named, schema-bounded capability. |
| Human operator | Approves the required tier and handles excluded interactive credential edges. |
| GitHub/CI | Coordinates review and receives audit evidence. |
| Android device | Executes only the bounded local operation. |

## See

- Source: [`docs/architecture/termux-agentic-hub.md`](../../../architecture/termux-agentic-hub.md)
