# Termux Agentic Hub — Design

> **Evidence status:** capability boundary defined; user experience map candidate  
> **Design owner:** Termux Agentic Hub maintainers  
> **Canonical implementation:** `hub_mcp/` and linked contracts  
> **Last source review:** 2026-11-23

## 1. Purpose and users

The repository architecture identifies the Hub as the Android/Termux execution hub. Its capability and transport boundaries are defined by the linked architecture and ICM sources. This design entry separates the underlying hub from the operator clients that present it.

## 2. Experience surfaces

| Surface | Audience | Evidence status | Owning source |
|---|---|---|---|
| Termux Agentic Hub capability surface | Local agents / operators | Contract defined | [Hub architecture](../../../architecture/termux-agentic-hub.md) |
| Platform/device boundary | Operators and maintainers | ICM mapped | [Platform ICM card](../../../icm/objects/platform/termux-agentic-hub.md) |
| ArchWiz client | Operators | Separate design entry | [ArchWiz design](../archwiz/design.md) |

## 3. Information architecture

The current source set defines a capability boundary, not a complete end-user navigation hierarchy. Keep hub capabilities distinct from client menus and dashboard groupings.

## 4. Journeys and interactions

Document interactions at the client that invokes each capability. The hub contract remains authoritative for capability semantics, transport, and execution boundaries.

## 5. Visual language

The hub is an execution/service surface. Visual presentation belongs to its clients and is documented in their system entries.

## 6. Accessibility

Record device-side accessibility and operator interaction constraints at the client surface. The current hub architecture source does not establish a complete user-interface accessibility contract.

## 7. Evidence and system states

Use the hub architecture, session schema, and transport/identity decision for capability and session semantics. Client displays should distinguish service availability from task completion.

## 8. Decisions and open gaps

- Inventory user-visible hub capabilities and the client that exposes each.
- Map capability states to client-visible status and recovery guidance.
- Establish whether the hub has any direct user interface of its own.
- Link tests for capability availability and failure behavior.

## 9. Canonical sources

- [Hub architecture](../../../architecture/termux-agentic-hub.md)
- [Platform ICM card](../../../icm/objects/platform/termux-agentic-hub.md)
- [Session SSOT](../../../schemas/session-ssot.md)
- [Transport and identity decision](../../../architecture/transport-and-identity-decision.md)
