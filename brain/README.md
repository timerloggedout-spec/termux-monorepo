# termux-brain

Standalone, dependency-free Rust crate facade over the monorepo-root brain.rs source. This crate is the **typed reasoning kernel**, not the entire Termux monorepo Brain.

The repository-wide Brain is the cognitive coordination layer spanning 21 subsystem families. Its complete target taxonomy is in [TERMUX-MONOREPO-BRAIN-SUBSYSTEM-MAP.md](../docs/architecture/TERMUX-MONOREPO-BRAIN-SUBSYSTEM-MAP.md); the source-inspected owner and integration boundaries are in [TERMUX-MONOREPO-BRAIN-OWNERSHIP-MAP.md](../docs/architecture/TERMUX-MONOREPO-BRAIN-OWNERSHIP-MAP.md). The QUE/Delphi architecture RFP is [qdesk.brain-rs #5501](https://github.com/timerloggedout-spec/termux-monorepo/issues/5501).

## Use from another Rust crate

Add a path dependency relative to the consuming crate:

~~~toml
[dependencies]
termux-brain = { path = "../../brain" }
~~~

Implement StageBackend for the selected model/deterministic provider and PolicyGate for the existing authoritative policy adapter. Construct Brain with both adapters and a BrainConfig, then pass a BrainInput with the canonical orchestration/cycle/attempt identity.

## Specialist extensions

The `extensions` module defines a small, statically typed contract for domain-owned
specialists. A specialist crate implements `BrainExtension`; the existing host
composes that crate with `termux-brain` and routes an explicit domain request.
The root kernel does not depend on a specialist, dynamically load plugins, or
create a second capability registry.

The invocation context carries the existing orchestration/cycle/attempt identity.
Descriptor, contract-version, identity and domain checks fail closed before the
specialist is called. A specialist's evaluation error remains distinct from a
contract error.

## Boundaries

- Brain coordinates typed reasoning stages and returns a plan plus policy decision. Adaptive is the default mode and selects Fast, Standard or Deep depth from the intent-stage complexity assessment; explicit modes remain available.
- StageBackend may reason; it must not execute tools or persist memory.
- PolicyGate receives context provenance, stage records and degraded status, then delegates to existing capability/decision/completion policy. There is no allow-all default.
- Context is bounded and excludes Restricted, Secret and Unknown classifications.
- Reflection returns learning candidates; a governed memory adapter owns persistence.
- Ready means ready for handoff, not executed, completed, passed or promoted.
- The crate does not call a model, open a network connection, spawn a process or access the filesystem.

## Validation

~~~sh
cargo fmt --manifest-path brain/Cargo.toml -- --check
cargo check --manifest-path brain/Cargo.toml --all-targets
cargo test --manifest-path brain/Cargo.toml
cargo clippy --manifest-path brain/Cargo.toml --all-targets -- -D warnings
~~~

The package is intentionally not part of a root Cargo workspace. Consumers share the same root source through this facade.