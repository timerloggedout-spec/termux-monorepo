# QUE Device Validation Control Plane

**Canonical proposal:** [que-device-validation](../proposals/active/que-device-validation/)  
**Machine registry:** [ops/device-validation/registry.json](../../ops/device-validation/registry.json)  
**Diagram source:** [QUE-DEVICE-VALIDATION.mmd](QUE-DEVICE-VALIDATION.mmd)

## Authority boundaries

| Plane | Authority | Responsibility |
|---|---|---|
| Module owner | Module lane record | Defines target behavior, device dependencies, test suite and acceptance contract. |
| Tool registry | `ops/device-validation/registry.json` | Describes tool profiles, capabilities, provenance and verification state. |
| QUE | Existing QUE admission/dispatch system | Queue, tier, claim, lease, retry and execution routing. |
| Backend adapter | Registered adapter contract | Capability check, isolated execution, cleanup and evidence receipt. |
| DoE | Existing DoE family | Design and analyze controlled backend comparisons. |
| MoneyBall | Existing value/performance decision lane | Rank verified outcomes under declared constraints; retain uncertainty and Pareto alternatives. |
| Evidence envelope | `docs/ops/EVIDENCE-ENVELOPE.schema.json` | Canonical immutable observation provenance. |
| IDRR / Integration Intelligence | Existing registries | Index and reconcile capability/tool references; do not duplicate this registry. |
| Proposal + dual gates | Existing lifecycle | Review, validate and promote repository changes. |

## Operating sequence

1. A module change identifies its own lane ID and test requirements.
2. RECON resolves compatible registered profiles and refreshes availability evidence.
3. The capability resolver returns eligible profiles, rejected profiles and reasons.
4. QUE applies its own admission and dispatch policy.
5. A backend executes the module's allowlisted suite in a disposable environment.
6. The adapter emits an evidence envelope tied to the immutable target SHA and backend fingerprint.
7. The lane classifies product failure, harness failure, environment failure, capability mismatch or incomplete evidence.
8. DoE/MoneyBall consumes comparable observations and recommends retain/cull/expand.
9. Physical-device acceptance is performed when hardware or real Android behavior is required.
10. Promotion follows the existing proposal and dual-gate rules.

## State dimensions

Registration, implementation, discovery, verification and availability are separate dimensions. No one state implies another. A current availability observation must be scoped to the host/runtime and have a freshness expiry.

Validation states distinguish `QUE_ADMITTED`, `QUE_RUNNING`, `EMULATOR_PASS`, `EMULATOR_FAIL`, `DEVICE_REQUIRED`, `DEVICE_PASS`, `DEVICE_FAIL`, `NEED_EVIDENCE` and `PROMOTION_ELIGIBLE`. The state machine never maps emulator PASS directly to DEVICE_PASS.

## Module lane rule

Every independently owned device-dependent module has its own stable lane. A module lane can use multiple backends and suites. Shared tooling is registered once and referenced by lane. The registry coverage status remains partial until repository-wide RECON establishes the full denominator.

## What this does not assert

This design does not assert that an Android device, Termux MCP, AVD pool, QEMU host, Waydroid host, Termux Docker image, or dedicated emulator fleet is presently online. Those facts require fresh, attributable observations.
