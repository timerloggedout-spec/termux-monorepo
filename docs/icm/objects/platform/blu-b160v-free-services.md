# BLU B160V and Free-Services Envelope

| Field | Value |
|---|---|
| Type | object |
| Cluster | platform |
| Universe | live |
| Status | stale |
| Entity | The user-declared operating constraint: one Android BLU B160V device and free services only |

## What this is

This card records an **operator constraint**, not a device-health assertion. The user has declared the Android BLU B160V as the only device and free services as the only external-service tier for this repository. This documentation change does not connect to, inspect, schedule, or modify the device or its Termux MCP.

## Routing rule

When a future repository change proposes execution, automation, a visual layer, or an external integration, first confirm that it can operate within the declared envelope. Prefer local files, standard Termux capabilities, free-tier services, and optional/on-demand components. Do not assume a second host, paid service, always-on daemon, private endpoint, or device availability.

The next actual device-using change must re-verify the device and its current resource state through the established platform policy; this card intentionally remains `stale` until that evidence exists.

## First-order impact

**Hits:** platform/job design, service assumptions, optional visual review, and human validation scope.
**Does not hit:** the Termux MCP connection, device configuration, service credentials, or application code automatically.

## Evidence

[1] Operator constraint recorded in the active ICM proposal source note.
[2] [`termux-agentic-hub.md`](termux-agentic-hub.md) defines the existing Android/Termux execution boundary and governance path.
