# OSx Forge — Infrastructure Pattern Candidate

**Disposition:** metadata-only pattern harvest; source-level review pending  
**Category:** `refTemplates/10_Infrastructure/`  
**Upstream:** https://github.com/credkellar/OSx  
**Evidence snapshot:** Docker Hub overview at https://hub.docker.com/r/credkellar/osx (reviewed 2026-11-23)

## Scope

The Docker Hub overview describes two related components:

- **Forge (`OSx/`):** a zero-dependency Rust builder that parses a strict TOML manifest, constructs a dependency graph, records SHA-256 input identities in a deterministic lockfile, and plans sandboxed builds, cross-compilation, image assembly, and deployment.
- **OS (`custom-os-root/`):** an immutable-core microkernel design with A/B update and rollback, sandboxed applications, deduplicated storage, ARC caching, LZ4 blocks, a DPDK path, TPM-backed key handling, executable-format parsing, capability permissions, and an on-device AI daemon.

## Evidence boundary

The upstream GitHub repository could not be fetched through the connected GitHub source reader during this review. The feature summary and status below therefore reflect the Docker Hub package overview, rather than independent source inspection.

The package overview labels the project early-stage. It reports parser, dependency graph, lockfile, and delta-updater logic as unit-tested. It describes sandbox, image assembly, and PXE deployment as deterministic planning rather than execution; PXE flashing is gated behind an unset `arm` flag. It describes ARC, LZ4, executable-header parsing, page allocation, and swap state logic as implemented pure logic, while TPM transport and the LLM runner remain plan/spec modules.

## Candidate patterns for repository adaptation

| OSx pattern | Repository adaptation candidate | Admission state |
|---|---|---|
| Strict TOML manifest | Typed, validated capability/build manifests | Research candidate |
| SHA-256 deterministic lockfile | Content-addressed dependency and artifact provenance | Research candidate |
| Explicit dependency graph | Reproducible task/build DAG with declared inputs | Research candidate |
| Sandbox build plan | Dry-run-first isolated execution with explicit promotion evidence | Compare with existing sandbox and dual-gate contracts |
| Immutable core + A/B rollback | Versioned protected contracts and reversible artifact promotion | Research candidate |
| Delta updates | Minimal, hash-verified repository reconciliation | Research candidate |

## Explicit exclusions from current adoption

- Treat DPDK, TPM, microkernel, storage-cache, and on-device AI claims as upstream research only.
- Treat ISO assembly, namespace isolation, PXE flashing, and hardware execution as planned capabilities until independently demonstrated.
- Create no live `smods/` gitlink from this metadata record.
- Promote no implementation from feature descriptions alone.

## Validation path

1. Retrieve and inspect the upstream source tree, license, tests, and release history.
2. Reproduce the manifest parser, dependency graph, and lockfile behavior in a bounded test harness.
3. Compare candidate patterns against existing provenance, sandbox, artifact, rollback, and dual-gate contracts.
4. Record an adaptation proposal with source revision, evidence, compatibility impact, and test results.
5. Consider a custom fork or live pin only after license review, immutable pinning, compatibility evidence, and the existing dual-gate.

**Current result:** pattern candidate recorded; implementation adoption remains pending.
