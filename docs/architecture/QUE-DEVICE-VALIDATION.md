# QUE Device Validation Control Plane

**Status:** proposal implementation; module census and runtime fleet validation remain incomplete  
**Owner/lane:** QUE Device Validation · module-owned device lanes  
**Canonical for:** module-per-lane validation contracts and tool-profile registration  
**Proposal:** [que-device-validation](../proposals/active/que-device-validation/)  
**Registry:** [ops/device-validation/registry.json](../../ops/device-validation/registry.json)  
**Diagram:** [QUE-DEVICE-VALIDATION.mmd](QUE-DEVICE-VALIDATION.mmd)

## Authority boundaries

| Plane | Canonical authority | Responsibility |
|---|---|---|
| Module owner | Module lane record | Defines target behavior, device dependencies, suites and acceptance contract. |
| Tool registry | `ops/device-validation/registry.json` | Describes tool profiles, capabilities, provenance and independent state dimensions. |
| Cadence admission | Existing admission surface + `ops/quota/dispatch-tiers.json` | Admission thresholds, tier policy and queue-pressure deferral. |
| QUE / dispatch machinery | Existing task ranking, dispatch watchdog and claim/lease machinery | Rank, claim, lease, reclaim and escalation. |
| Claimable routes | `ops/dispatch/claimable-routes.json` + registered workflows | Allowlisted execution triggers and attributable run receipts. |
| QUE feeds | `ops/que/feeds/` | Read-model projections; not a task-dispatch API. |
| Backend adapter | Registered adapter contract | Capability check, isolated execution, cleanup and evidence receipt. |
| DoE | Existing DoE family | Design and analyze controlled backend comparisons. |
| MoneyBall | Existing value/performance lane | Compare verified outcomes while retaining uncertainty and Pareto alternatives. |
| Evidence envelope | `docs/ops/EVIDENCE-ENVELOPE.schema.json` | Canonical immutable observation provenance. |
| IDRR / Integration Intelligence | Existing registries | Index and reconcile references; do not duplicate their authority. |
| Proposal + dual gates | Existing lifecycle | Review, validate and promote repository changes. |

The device-validation proposal adds a capability registry and adapter contract. It does **not** add a queue, scheduler, admission controller, lease manager, event ledger, generic experiment schema or CMDB.

## Operating sequence

1. A module change identifies its own stable lane ID and required test suites.
2. RECON resolves compatible registered profiles and refreshes environment-scoped availability evidence.
3. The capability resolver returns eligible profiles, rejected profiles and explicit reasons.
4. The existing intake route files the bounded task; Cadence applies its admission and tier policy.
5. QUE ranking/claim/lease/watchdog machinery assigns the task, and a registered claimable route fires the allowlisted workflow.
6. A backend executes the module's allowlisted suite in a disposable environment.
7. The adapter emits a SHA-bound evidence envelope tied to the module lane and backend fingerprint.
8. The lane classifies product failure, harness failure, environment failure, capability mismatch or incomplete evidence.
9. DoE/MoneyBall consumes comparable observations and recommends retain/cull/expand.
10. Physical-device acceptance is performed whenever hardware or real Android behavior is required.
11. Promotion follows the existing proposal lifecycle and dual-gate policy.

## State dimensions

Registration, implementation, discovery, verification and availability are independent dimensions. No one state implies another. A current availability observation must identify its host/runtime, profile version, observation time and expiry.

Execution/validation states distinguish:

- `QUE_ADMITTED` and `QUE_RUNNING`;
- `EMULATOR_PASS` and `EMULATOR_FAIL`;
- `DEVICE_REQUIRED`, `DEVICE_PASS` and `DEVICE_FAIL`;
- `NEED_EVIDENCE` and `PROMOTION_ELIGIBLE`.

The state machine never maps emulator PASS directly to DEVICE_PASS. A hardware-required lane cannot be promoted from emulator evidence alone.

## Module lane rule

Every independently owned device-dependent module has its own stable lane. A lane may use multiple backends and suites. Shared tooling is registered once and referenced by lane. The registry coverage status remains `partial` until repository-wide RECON establishes the complete module denominator and owner reconciliation closes the gaps.

## Backend fit

| Backend | Appropriate validation | Boundary |
|---|---|---|
| Android AVD | APK install/launch, Android API behavior, permissions, lifecycle and UI/WebView checks | Not OEM or physical hardware parity |
| Termux-native device | Real Termux package/runtime paths and Android integration | Requires a currently verified, authorized device |
| Termux Docker / Linux container | Portable shell, language/runtime and filesystem behavior | Not Android framework or app sandbox parity |
| QEMU | CPU/ABI, guest OS, kernel and architecture workloads | Not Android UI/API parity without a separately proven Android guest |
| Waydroid | Selected Android userspace/app compatibility on supported Linux hosts | Not physical device/OEM parity |
| Physical Android device | Sensors, USB, Bluetooth, battery/thermal, radios, OEM power and real lifecycle | Requires device-lab authorization and safe reset |

## What this does not assert

This design does not assert that an Android device, Termux MCP, AVD pool, QEMU host, Waydroid host, Termux Docker image or dedicated emulator fleet is presently online. Those facts require fresh, attributable observations. Existing StudySprint AVD and Termux smoke implementations are verified repository assets; their current execution availability remains per-run evidence.
