# ITEMS — que-device-validation

| ID | Priority | Status | Scope | Acceptance criteria |
|---|---:|---|---|---|
| QDV-001 | P1 | executing | Register module-per-lane architecture, authority boundaries and staged rollout. | Every device-dependent module has its own stable lane ID; no central mega-lane; QUE remains dispatch authority; hardware-only work cannot be emulator-promoted. |
| QDV-002 | P1 | executing | Formalize tool and machine-profile registration for future RECON. | Versioned JSON registry + strict schema; separate declared/discovered/verified/available states; evidence and provenance required; no credentials or secret values. |
| QDV-003 | P1 | executing | Register initial verified examples and explicit unknowns. | StudySprint AVD and Termux smoke are evidence-backed; QEMU, Waydroid, Termux Docker and physical-device availability remain unverified until observed; planned components are not mislabeled implemented. |
| QDV-004 | P1 | executing | Implement deterministic registry validator and tests. | Stdlib validator checks IDs, required fields, lifecycle enums, tool references, module-lane uniqueness and evidence references; unit tests cover valid and invalid fixtures. |
| QDV-005 | P1 | executing | Define QUE task/admission/receipt integration without a parallel scheduler. | QUE receives lane ID, target SHA, capabilities, backend constraints and evidence policy; lease/claim authority remains QUE; receipts bind immutable execution provenance. |
| QDV-006 | P1 | executing | Pre-register DoE/MoneyBall comparison method. | Compare QUE-native, QUE+specialist and dedicated-fleet strategies on common cohorts; hard safety/correctness gates precede Pareto/value scoring; no invented scores. |
| QDV-007 | P1 | executing | Publish high-detail architecture, Mermaid source, RECON runbook and operational contracts. | Architecture, state machine, decision matrix, onboarding template, threat model, failure modes and rollout stages documented with source links. |
| QDV-008 | P1 | queued | Integrate registry validation into the owning CI / QUE intake path. | Existing CI and QUE interfaces are mapped; workflow ownership/permissions confirmed; path-filtered checks pass on exact SHA; no duplicate poller or event ledger. |
| QDV-009 | P1 | queued | Inventory all device-dependent modules and register each lane. | Bounded RECON scan reconciles module paths, package manifests, Android APIs, device scripts, hardware dependencies and existing test harnesses; coverage report records exclusions and unresolved candidates. |
| QDV-010 | P1 | queued | Execute controlled emulator/backend benchmark and establish MoneyBall ranking. | Pre-registered cohort, repeated trials, immutable evidence envelopes, cost/latency/reliability/fidelity metrics, uncertainty and Pareto report; no backend promotion from unverified claims. |

## Validation

- `python3 scripts/device_validation/validate_registry.py`
- `python3 -m unittest tests.test_device_validation_registry -v`
- `python3 scripts/proposals/validate_registry.py`
- `python3 scripts/ci/repo_gate.py`
- `python3 scripts/ci/termux_smoke.py`

## Status semantics

QDV-001–007 are the bounded foundation implementation. QDV-008–010 remain queued because they require integration with existing CI ownership, a complete repository-wide module census, and runtime benchmark evidence. A documentation/schema implementation does not claim those operational outcomes.
