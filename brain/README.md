# termux-brain

Standalone, dependency-free Rust crate facade over the monorepo-root brain.rs source.

## Use from another Rust crate

Add a path dependency relative to the consuming crate:

~~~toml
[dependencies]
termux-brain = { path = "../../brain" }
~~~

Implement StageBackend for the selected model/deterministic provider and PolicyGate for the existing authoritative policy adapter. Construct Brain with both adapters and a BrainConfig, then pass a BrainInput with the canonical orchestration/cycle/attempt identity.

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