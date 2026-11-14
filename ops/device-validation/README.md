# Device Validation Registry

This is the repository's **device-test capability catalog**, not a scheduler or device inventory database.

- Machine-readable source: [`registry.json`](registry.json)
- Contract: [`registry.schema.json`](registry.schema.json)
- Architecture: [`docs/architecture/QUE-DEVICE-VALIDATION.md`](../../docs/architecture/QUE-DEVICE-VALIDATION.md)
- Proposal / acceptance ledger: [`docs/proposals/active/que-device-validation/`](../../docs/proposals/active/que-device-validation/)

## Register a tool for future RECON

1. Identify the exact upstream project, canonical URL, immutable release/tag/commit, license and retrieval date.
2. Create a stable `tool_profile_id`; never reuse an ID for a materially different tool or adapter.
3. Record host/guest platforms, supported architectures, Android API levels, Termux constraints, required privileges and declared capabilities.
4. Record unsupported capabilities explicitly. Do not infer broad Android/Termux parity from a Linux smoke test.
5. Add a reproducible install/build identity, version probe, healthcheck, representative smoke suite and reset/disposal contract.
6. Record network egress, mounted paths, secret handling, data retention, isolation and resource limits.
7. Attach source evidence and runtime observation references. Keep credentials and personal device identifiers out of Git.
8. Set registration, implementation, discovery, verification and availability states independently.
9. Run `python3 scripts/device_validation/validate_registry.py` and the focused tests.
10. Request independent review. A registration becomes a routing candidate only after the required evidence is verified.

## State meanings

| Dimension | Values | What it proves |
|---|---|---|
| registration | proposed / registered / retired | A record exists and has lifecycle ownership. |
| implementation | absent / planned / implemented | Adapter or harness implementation status. |
| discovery | not_checked / discovered / not_found | A bounded source/host discovery was performed. |
| verification | unverified / verified / failed / stale | Contract tests were run against a specific version/context. |
| availability | unknown / available / unavailable / degraded | A fresh observation in one named execution context. |

A registry row is not a health check. Availability observations must include observed time, expiry, host/runtime identity, profile version and evidence pointer.

## Register a module lane

Each independently owned device-dependent module receives one stable `module_lane_id`. Its lane declares target contracts, test suites, required and forbidden capabilities, hardware-only requirements, preferred profiles, evidence policy, reset procedure and owner.

Shared test tools belong in `tool_profiles`; do not copy the same tool into each module lane. A lane may reference multiple profiles for different suites.

## Current validation

```bash
python3 scripts/device_validation/validate_registry.py
python3 -m unittest tests.test_device_validation_registry -v
```

## Initial inventory caveat

The registry is an initial, source-backed seed, not a complete module census. `inventory.coverage=partial` remains until repository-wide RECON reconciles all device-dependent modules and their owning teams. Missing modules are not assumed to be absent.
