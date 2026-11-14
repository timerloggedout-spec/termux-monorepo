---
type: object
cluster: platform
universe: live
status: proposed
entity: QUE device-validation control plane
verified_at: 2026-11-14
---

# QUE Device Validation

The **QUE Device Validation** design gives each independently owned device-dependent repository module its own validation lane. QUE remains the umbrella dispatch/assurance domain. Cadence owns admission/tiering, dispatch machinery owns rank/claim/lease/watchdog, and registered claimable routes own executable triggers. Backend tools are registered capabilities, not schedulers.

## Existing QUE integration sources\n\n- [QUE auto-claim and lease contract](../../../../docs/ops/QUE-AUTO-CLAIM.md)\n- [Claimable route registry contract](../../../../docs/ops/CLAIMABLE-ROUTES.md)\n- [Queue dependency tiers](../../../../docs/ops/QUEUE-DEPENDENCY-TIERS.md)\n\n## Canonical sources

- Architecture: [QUE-DEVICE-VALIDATION.md](../../../../docs/architecture/QUE-DEVICE-VALIDATION.md)
- Mermaid source: [QUE-DEVICE-VALIDATION.mmd](../../../../docs/architecture/QUE-DEVICE-VALIDATION.mmd)
- Tool and module registry: [ops/device-validation/registry.json](../../../../ops/device-validation/registry.json)
- Registration and RECON procedure: [QUE-DEVICE-VALIDATION-RECON.md](../../../../docs/ops/QUE-DEVICE-VALIDATION-RECON.md)
- Proposal and implementation ledger: [que-device-validation](../../../../docs/proposals/active/que-device-validation/)

## Current status boundary

This is a proposed/implementing architecture and an initial partial registry. It does not establish a live Android device, Termux MCP session, QEMU host, Waydroid runtime, Termux Docker image, or general emulator fleet. The historical Termux Agentic Hub card remains stale and is not evidence of current device availability.

## If you change this

- **Hits:** device-validation registry schema, tool profiles, module lane declarations, QUE adapter contract, DoE/MoneyBall comparison, evidence receipts, architecture docs and relevant module-owned test harnesses.
- **Does not hit:** QUE's existing scheduler/claim authority, generic CI workflow ownership, physical-device provisioning or production deployment without separately approved integration work.

## RECON rule

Treat registration, implementation, discovery, verification and availability as separate dimensions. A profile becomes eligible for routing only when its required capability claims are backed by current evidence and the module lane accepts its compatibility envelope. Emulator PASS never becomes physical-device PASS.
