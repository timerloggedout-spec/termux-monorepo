# QUE Device Validation — Technical Design

**Proposal:** `que-device-validation`  
**Status:** executing foundation; runtime fleet and exhaustive module census not yet established  
**Date:** 2026-11-14

## 1. Decision

Adopt **QUE + specialist backends** as the architecture to evaluate, not as a pre-proven performance winner.

- QUE remains the sole admission, scheduling, claim/lease, retry and task-dispatch authority.
- Each device-dependent repository module owns one independently addressable validation lane.
- A shared capability registry describes tool backends and machine profiles; it does not schedule or claim work.
- DoE/MoneyBall compares backend strategies on matched workloads and chooses by verified outcomes, not brand preference.
- Emulator PASS is a pre-device result. It cannot satisfy a hardware acceptance requirement or be represented as physical-device PASS.

## 2. Scope and non-goals

### In scope
- Android APK/app modules, Termux-native scripts and services, device queue/poller modules, Android APIs, hardware interfaces, device-bound agents, and any future repository module whose behavior depends on a device/runtime capability.
- Tool/machine profile registration, recon discovery, module-lane contracts, test admission, evidence receipts, backend selection inputs, experiment design and comparison.
- Existing AVD and Termux smoke paths as initial registered examples.

### Non-goals
- Replacing QUE, DoE, MoneyBall, ATES, IDRR, Integration Intelligence, the proposal registry or GitHub Actions.
- Claiming a live device, tunnel, MCP, emulator pool, cloud account, runner, or installed tool without fresh evidence.
- Treating Linux container success as Android/Termux parity.
- Emulating sensors, USB, Bluetooth, battery/thermal behavior, OEM power management, radio/modem behavior or Play Services behavior unless a specific backend demonstrably reproduces the target contract.
- Automatically provisioning paid infrastructure or spending provider credits.
- Unbounded remote shell, arbitrary device control, credential export or secrets in registry/evidence.

## 3. Layered architecture

### 3.1 Module lane
Each module gets a stable ID such as `device-lane:apps.studysprint.android`. Its lane record declares:
- owning module path and owner;
- target platforms, API levels, ABIs and runtime constraints;
- device dependencies and capability requirements;
- test suites, entrypoints, test data class and expected outcomes;
- backend compatibility rules and excluded capabilities;
- hardware-only requirements and escalation route;
- reset/cleanup contract;
- required evidence envelope and independent review;
- lane lifecycle and coverage status.

A module may have multiple test profiles, but only one canonical module lane identity per independently owned component. Shared test utilities are registered as tool profiles, not duplicated as module lanes.

### 3.2 Tool and machine profile registry
`ops/device-validation/registry.json` is the domain registry for test-backend profiles and module-lane declarations. `registry.schema.json` defines its contract. It stores references and declarative metadata only.

The registry distinguishes:
- `registration_state`: proposed / registered / retired;
- `implementation_state`: absent / planned / implemented;
- `discovery_state`: not_checked / discovered / not_found;
- `verification_state`: unverified / verified / failed / stale;
- `availability_state`: unknown / available / unavailable / degraded.

These are orthogonal. A profile can be registered and implemented while current availability remains unknown. Fresh availability is scoped to a specific execution context and expires.

### 3.3 QUE orchestration
QUE receives a bounded job contract containing:
`task_id`, `module_lane_id`, `target_sha`, `suite_id`, `required_capabilities[]`, `preferred_tool_profiles[]`, `forbidden_capabilities[]`, `hardware_required`, `resource_budget`, `deadline`, `evidence_policy_ref`, and `idempotency_key`.

QUE applies its existing admission, tier, queue-pressure, claim/lease and dispatch rules. The device-validation adapter returns a backend recommendation and compatibility explanation; it never independently enqueues, claims, retries or promotes a task. If current QUE contracts cannot carry a field, that gap becomes a separately reviewed integration item rather than an undocumented side channel.

### 3.4 Execution backends
Backends implement a common adapter contract:
1. resolve a registered profile;
2. verify current availability and version/image identity;
3. check required capabilities and exclusions;
4. create an isolated run context;
5. execute only the module's allowlisted test entrypoint;
6. collect logs/results and redact sensitive data;
7. reset/dispose the environment;
8. emit a SHA-bound evidence receipt.

### 3.5 Evidence and promotion
Reuse `docs/ops/EVIDENCE-ENVELOPE.schema.json` and the DoE experiment record schema. Evidence must bind:
- repository commit and baseline SHAs;
- QUE task/run identity and attempt;
- module lane + test suite + backend profile IDs;
- emulator/OS image digest, Android API, ABI/CPU architecture and tool versions;
- test command/entrypoint identity and test-data fixture version;
- started/finished timestamps, exit/result, logs/artifact references and hashes;
- cleanup/reset result, resource use, cost (or explicit unknown), provenance and confidence.

States remain distinct: `COMMITTED`, `EXECUTED`, `VALIDATED`, `DEVICE_ACCEPTED`, `PROMOTED`. A successful emulator run sets only the applicable emulator validation state. A hardware-required module needs a separate physical-device acceptance record.

## 4. Backend taxonomy and routing

| Backend | Best fit | Not sufficient for |
|---|---|---|
| Termux-native device | Real Termux package paths, Android app integration, device APIs and actual Android lifecycle. | High-concurrency cheap CI or repeatable fleet capacity unless provisioned. |
| Android Studio AVD / Android Emulator | Android API behavior, APK install/launch, permissions, lifecycle, WebView/UI, API-level regression. | OEM-specific behavior, physical radios, sensors, battery/thermal, arbitrary hardware. |
| Termux Docker / proot-like Linux | Shell/Python/Node behavior, package layout, path/permission assumptions that are faithfully represented by the image. | Android framework, Bionic/Android linker behavior, Android permission model, background limits. |
| QEMU system/user emulation | CPU/ABI/architecture, boot/kernel/rootfs and cross-architecture tests when configured. | Android UI/API fidelity unless an Android guest image and harness are separately proven. |
| Waydroid | Linux-hosted Android userspace and selected app compatibility scenarios. | Physical Android hardware/OEM behavior; availability on a supported runner must be proven. |
| Physical Android device | Hardware APIs, OEM behavior, radios, sensors, battery, thermal, real Termux, real power/background behavior. | Large, cheap, deterministic parallel test matrix without a managed lab. |
| Generic Linux container/VM | Fast unit/integration tests and deterministic CLI behavior. | Termux or Android parity unless the module contract is limited to portable Linux behavior. |

Routing is capability matching, not one-backend-per-module. Each module lane may choose multiple backends for different test classes.

## 5. Capability vocabulary

Initial capability identifiers:
- `android.apk.install`
- `android.activity.launch`
- `android.permission.runtime`
- `android.lifecycle.background`
- `android.webview.render`
- `android.api.level.<n>`
- `android.abi.<abi>`
- `termux.prefix.layout`
- `termux.package.environment`
- `termux.api.bridge`
- `linux.shell`
- `linux.filesystem.permissions`
- `cpu.arch.<arch>`
- `kernel.boot`
- `usb.device`
- `bluetooth.device`
- `sensor.<kind>`
- `battery.thermal`
- `radio.modem`
- `oem.power-management`
- `physical.android.device`

A backend advertises only capabilities with evidence. Capability matching must include version, platform and confidence; a broad `android=true` flag is insufficient.

## 6. Formal RECON tooling registration

Every future tool/backend candidate enters through a registration record:
1. stable `tool_profile_id` and canonical upstream identity;
2. exact upstream repository, release/tag/commit, license and retrieval date;
3. tool family and adapter interface version;
4. supported host/guest OS, architecture, Android API, Termux version and required privileges;
5. declared capabilities, exclusions and compatibility matrix;
6. installation/provisioning method and reproducible image/build fingerprint;
7. healthcheck, smoke test, version probe and reset/disposal procedure;
8. security model: privilege, network egress, mounted paths, secrets handling, data retention and isolation;
9. resource envelope: CPU, RAM, disk, startup latency, concurrency and cost basis;
10. evidence URLs, hashes, observed environment, last verified time and expiry;
11. lifecycle states and next RECON action.

Tool claims are not accepted from a README alone. A future RECON performs:
- static provenance/license/dependency inspection;
- release and advisory check;
- compatibility review against target modules;
- sandboxed install/build where permitted;
- healthcheck + representative smoke;
- isolation/egress/secret-retention review;
- measured resource and reset test;
- evidence capture and independent classification.

No tokens, cookies, private keys, device identifiers that expose a person, or raw session stores belong in the registry.

## 7. Initial registered examples and confidence

The initial registry contains:
- StudySprint Android AVD workflow: implementation verified in repository; current AVD runner availability is per-run and not inferred.
- Termux smoke: implementation verified; its scope is runtime-surface smoke, not full Android-device parity.
- Termux Docker, QEMU, Waydroid and physical Android device: candidate profiles; availability and installation are unverified in this implementation.
- StudySprint and Termux runtime: initial module lanes. Device queue poller and Game Player Machines are declared planned/documentation-backed lanes where source supports the plan; not marked implemented.

The inventory coverage field remains `partial` until a bounded repository scan and owner reconciliation account for every device-dependent module.

## 8. DoE / MoneyBall experiment design

Compare three strategies:
- **A — QUE-native:** current existing backends and workflows, no new fleet.
- **B — QUE + specialist backends:** QUE remains the control plane; select AVD, Termux Docker, QEMU, Waydroid or physical device only when capability match and evidence justify it.
- **C — dedicated emulator fleet:** managed reusable machines/images with reset, health, telemetry and concurrency controls.

Use matched module × suite × commit cohorts. Block by module, target API/ABI, test class, runner class and workload difficulty. Randomize backend order within feasible blocks. Repeat enough trials to estimate variance; preregister sample size/stopping and missing-data rules before interpreting results. Keep a native baseline and a physical-device comparator for hardware-relevant suites.

### Hard gates (non-compensatory)
- test correctness and target-contract fidelity;
- isolation, security and privacy;
- reproducible environment identity;
- evidence completeness and immutable SHA linkage;
- no unsupported capability substitution;
- successful cleanup/reset;
- explicit physical-device acceptance for hardware-only requirements.

Any hard-gate failure excludes an arm from promotion regardless of speed or cost.

### Outcomes / metrics
- validated defect detection rate against seeded/known defects;
- false-positive and false-negative rate where labels exist;
- module/test capability coverage;
- emulator-to-device disagreement rate;
- test pass reliability and flake rate;
- median and p95 queue wait, startup, execution and total feedback latency;
- cost per valid test run and cost per confirmed defect caught;
- CPU/RAM/disk peak and concurrency efficiency;
- reset success and recovery time;
- maintenance hours, image drift, adapter failure rate;
- evidence completeness and reproducibility.

### MoneyBall method
First publish raw metrics, uncertainty intervals and Pareto fronts. Only after baseline variance and operator priorities are known should a composite value score be preregistered. Do not invent weights or collapse correctness, fidelity and cost into one opaque number. Preserve the full metric vector and the rationale for every cull/retain decision.

A backend wins only if it improves a relevant outcome without violating a hard gate and without imposing a worse total cost/maintenance frontier. A combination may win if interaction benefit exceeds integration and operational complexity.

## 9. Safety and trust boundaries

- Test jobs run in disposable, least-privilege environments with allowlisted commands.
- No arbitrary shell from a queue payload; task schema names a registered suite and entrypoint.
- Secrets are runtime-injected by approved secret managers and never serialized into receipts.
- Device-local MFA, personal profiles and human-only provider flows remain outside unattended CI.
- Network egress is denied by default and allowlisted per suite.
- Test fixtures are synthetic or explicitly approved; personal data is excluded.
- Emulator snapshots are treated as sensitive if they contain accounts, tokens or user data.
- Logs/screenshots/UI dumps are redacted before upload.
- Hardware operations require explicit device-lab authorization and safety interlocks.
- External tool output and downloaded images are untrusted inputs.

## 10. Failure and fallback model

| Failure | Classification | Response |
|---|---|---|
| Profile not registered | admission failure | Block and open RECON intake; no guessed backend. |
| Registered but not discovered | discovery gap | Run bounded discovery; keep unavailable/unknown. |
| Backend absent or unhealthy | capacity failure | QUE re-evaluates eligible alternatives; record skip/block, not test PASS. |
| Capability mismatch | compatibility failure | Reject backend; route to another profile or physical device. |
| Image/version drift | reproducibility failure | Pin/rebuild profile; invalidate incomparable results. |
| Emulator test fails | product or environment finding | Preserve logs; classify harness vs product fault; don't auto-rerun blindly. |
| Cleanup/reset fails | isolation failure | Quarantine machine/profile until reset is verified. |
| Device-only requirement | hardware boundary | Set `DEVICE_REQUIRED`; emulator result cannot promote. |
| Evidence incomplete | validation failure | Mark `NEED_EVIDENCE`; no promotion. |
| Queue pressure | admission/capacity | QUE applies existing tier/lease policy; no shadow queue. |

## 11. Rollout

1. **Foundation:** land proposal, schema, registry, validator, docs and examples.
2. **Inventory:** enumerate module lanes from repository paths and owning component manifests; resolve duplicates and omissions with module owners.
3. **Adapter contract:** map current QUE job schema and existing evidence envelope; implement a thin, read-only capability resolver.
4. **CI integration:** add path-filtered validation to the owning existing workflow only after workflow permission/ownership review.
5. **Pilot:** StudySprint Android AVD + Termux runtime suite; establish native and device comparator where available.
6. **DoE campaign:** run A/B/C strategies with frozen cohort and preregistered metrics.
7. **Scale:** add module lanes and backends incrementally; create dedicated fleet only if measured Pareto benefit justifies it.

## 12. Acceptance and promotion

Foundation acceptance: schema validates; registry validator passes tests; all initial claims have evidence classification; proposal registry validates; documentation links resolve; repo-gate and termux-smoke pass on the same PR SHA.

Operational acceptance is separate: all device-dependent modules are inventoried; QUE integration is proven; backend health and run receipts are observed; DoE campaign has valid sample and analysis; physical-device acceptance is captured for hardware-bound modules.

**A proposal merge is not an emulator fleet deployment.** A merged registry makes capabilities available for registration and recon; it does not claim any candidate backend is installed or currently available.
