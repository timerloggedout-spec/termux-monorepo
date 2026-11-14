# QUE Device Validation — RECON & Tool Registration

**Registry:** `ops/device-validation/registry.json`  
**Schema:** `ops/device-validation/registry.schema.json`  
**Registration template:** `ops/device-validation/registration-template.json`  
**Validator:** `scripts/device_validation/validate_registry.py`

## RECON objective

Discover tools and machine profiles that can validate a specific module contract. The unit of research is a **capability × module × environment**, not a vendor name or an emulator popularity ranking.

## Collection sequence

1. **Resolve the module lane.** Identify the owning module, exact paths, target runtime, test suites, API/ABI requirements and hardware-only dependencies.
2. **Search existing repo first.** Inspect current scripts, workflows, package manifests, ICM cards, issues, proposals and prior benchmark evidence. Reuse existing harnesses.
3. **Identify candidate tool.** Capture canonical upstream URL, repository, license, immutable release/tag/commit, maintainers, retrieval time and provenance.
4. **Inspect compatibility.** Host OS/kernel, guest OS, architecture, Android API, Termux package model, Bionic/glibc assumptions, privileges, KVM/namespaces, filesystem behavior and network model.
5. **Inspect security.** Process isolation, kernel sharing, mounts, device passthrough, egress, secrets, test accounts, telemetry, snapshots and artifact retention.
6. **Define capability claims.** Each claim must be narrow and falsifiable. Add exclusions and known limitations.
7. **Prove implementation.** Build/install in a disposable environment; record exact image/build fingerprint and tool version.
8. **Prove behavior.** Run healthcheck plus one representative workload from the module lane; preserve logs and result hashes.
9. **Prove reset.** Demonstrate disposal/reset and verify no test state, credential or account data survives.
10. **Measure operations.** Startup, execution, p50/p95 latency, CPU/RAM/disk, concurrency, failure rate, queue wait, cost and operator maintenance.
11. **Review and classify.** Mark each field verified/candidate/unknown/stale. Request independent review before the profile becomes an eligible routing candidate.
12. **Reconcile.** Re-fetch upstream and runtime evidence after expiry or material version/host change.

## Tool state contract

| State dimension | Allowed values | Promotion condition |
|---|---|---|
| Registration | proposed, registered, retired | Valid record and owner |
| Implementation | absent, planned, implemented | Adapter/harness path exists and tests |
| Discovery | not_checked, discovered, not_found | Bounded host/source discovery with timestamp |
| Verification | unverified, verified, failed, stale | Representative test and evidence on exact version |
| Availability | unknown, available, unavailable, degraded | Timestamped runtime observation scoped to a named host/profile |

Availability expires. A profile with no fresh runtime observation remains `unknown`, even when its upstream project is healthy or its code is merged.

## Evidence minimum

Each verified runtime observation should include:
- source repository SHA and target module SHA;
- tool profile ID, adapter version, image digest and host fingerprint;
- observed timestamp and expiry/freshness policy;
- capability probe and representative test result;
- resource measurements and cost basis;
- reset/cleanup result;
- redacted logs/artifact references and hashes;
- provenance kind, source URL, confidence and independent review.

Reuse `docs/ops/EVIDENCE-ENVELOPE.schema.json`. Reuse the DoE family experiment schema for experiment observations. This runbook does not define a parallel event or experiment envelope.

## Registration anti-patterns

- README claims treated as runtime verification.
- `installed=true` treated as currently available.
- Android AVD, QEMU and Waydroid treated as interchangeable.
- Linux container smoke represented as Termux or Android parity.
- Emulator PASS promoted to physical-device PASS.
- Tool profile copied into each module instead of referenced.
- Secret values, user tokens, cookies, device serials or raw personal screenshots committed.
- Missing metrics represented as zero.
- Stale evidence silently copied forward.

## Current RECON baseline

As of 2026-11-14:
- StudySprint AVD harness/workflow: implementation verified; current availability unknown until a run is observed.
- Termux smoke: implementation verified; its scope is limited to the runtime checks documented by the script.
- Termux Docker, QEMU and Waydroid: candidates, not verified as provisioned.
- Physical Android device: availability unknown; the historical Termux Agentic Hub ICM card is explicitly stale.
- Module inventory: partial; QDV-009 remains open.
