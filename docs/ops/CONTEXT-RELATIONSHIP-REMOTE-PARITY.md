# Context Relationship Remote Build, Processing, and Data Parity

Status: implementation contract for `feat/context-relationship-rust-acceleration`

## Decision

**Remote execution is the primary compute path. Local Termux/BLU B160V execution is a failsafe and controlled actuation surface.**

The accelerator must therefore be designed and documented around:

1. remote compile;
2. remote reproducible build;
3. remote deterministic processing;
4. parity of emitted CRG metadata/artifacts;
5. explicit database/data-model parity.

Local execution MUST NOT become the de facto production compute authority merely because an AArch64 device can run the accelerator.

## Execution hierarchy

```text
canonical CRG contract
        |
        +--> GitHub Actions / remote build + processing (primary)
        |
        +--> Termux / BLU B160V (failsafe / device-specific actions)
        |
        v
canonical metadata + parity contract
        |
        v
CRG / pointer fabric
```

The local plane is useful when remote execution is unavailable, for operator-directed diagnostics, or for narrowly scoped actions that explicitly require device-local capabilities. It is not the preferred bulk indexing/build/processing substrate.

## Remote compile/build/processing

The remote lane MUST execute the exact PR/ref under test:

```text
checkout exact SHA
  -> cargo fmt --check
  -> cargo check
  -> cargo test
  -> cargo clippy -- -D warnings
  -> cargo build --release
  -> deterministic fixture
  -> parity receipt
```

A successful local build is never substituted for remote compilation evidence.

The deterministic fixture validates canonical full BLAKE3-256 identity, compact-reference stability, frequency/cost policy, JSON protocol validity, and metadata-only output. The fixture is an execution proof, not a benchmark claim.

## Data / database parity

There is intentionally **one graph/data authority**. The Rust accelerator does not create a second database.

Parity therefore means agreement at the canonical CRG data-contract boundary:

- schema version;
- node/relationship identity;
- full content digest;
- compact-reference resolution;
- verified vs candidate relationship semantics;
- provenance;
- deterministic fixture output.

If a SQLite or other materialized database is introduced as an execution cache, it remains a derived store. Its parity receipt MUST compare schema version, migration identity, row/entity counts, and canonical content/artifact digests against the authoritative CRG projection. It MUST NOT become a second relationship authority.

No database parity claim may be made merely because two processes completed successfully.

## Termux / BLU B160V policy

The device plane is intentionally retained as a failsafe.

Allowed:
- operator-directed diagnostics;
- bounded emergency processing;
- device-specific actions;
- offline development;
- comparison against the remote deterministic fixture.

Not the default:
- bulk canonical indexing;
- canonical graph writes;
- authoritative database mutation;
- replacing remote CI/build evidence;
- silently diverging local compiler/toolchain behavior.

A local result that differs from the remote deterministic fixture is a **parity failure**, not a new canonical result.

## Promotion gate

The remote path is established only when:

1. remote compile succeeds;
2. remote release build succeeds;
3. remote deterministic processing succeeds;
4. parity receipt validates;
5. Python/reference contract remains green;
6. no second graph/database authority is introduced;
7. local fallback can reproduce the fixture or explicitly reports environment divergence.

State remains distinct:

```text
DESIGNED
  -> COMMITTED
  -> REMOTELY BUILT
  -> REMOTELY PROCESSED
  -> PARITY VALIDATED
  -> PROMOTION-ELIGIBLE
```

None of these states implies merge or production promotion.

## Non-goals

- Making Termux the production compute plane.
- Treating an AArch64 local build as CI evidence.
- Maintaining two competing CRG databases.
- Copying private session bodies into parity artifacts.
- Claiming database parity without a canonical schema/data comparison.
