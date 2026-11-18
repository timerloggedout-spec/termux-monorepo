# termux-brain

Standalone, dependency-free Rust crate facade over the monorepo-root brain.rs source. This crate is the **typed reasoning kernel**, not the entire Termux monorepo Brain.

The repository-wide Brain is the cognitive coordination layer spanning 21 subsystem families. The QUE/Delphi architecture RFP, [qdesk.brain-rs #5501](https://github.com/timerloggedout-spec/termux-monorepo/issues/5501), indexes the subsystem taxonomy and ownership map; those canonical map files are not present in this checkout.

## Use from another Rust crate

Add a path dependency relative to the consuming crate:

~~~toml
[dependencies]
termux-brain = { path = "../../brain" }
~~~

Implement StageBackend for the selected model/deterministic provider and PolicyGate for the existing authoritative policy adapter. Construct Brain with both adapters and a BrainConfig, then pass a BrainInput with the canonical orchestration/cycle/attempt identity.

## Specialist extensions

The `extensions` module defines a small, statically typed contract for domain-owned
specialists. A specialist crate implements `BrainExtension`; a future production
host is intended to compose that crate with `termux-brain` and route an explicit
domain request. The production host route is not wired in this change; host
ownership and the bridge contract still require verification.
The root kernel does not depend on a specialist, dynamically load plugins, or
create a second capability registry.

The invocation context carries the existing orchestration/cycle/attempt identity.
Descriptor, contract-version, identity and domain checks fail closed before the
specialist is called. A specialist's evaluation error remains distinct from a
contract error.

## MOSAIC specialist

The `mosaic-brain` crate lives at `archwiz/mosaic_brain/` and depends on
`termux-brain` through a local Cargo path. Its typed contract and pure adapter
are present, but the production host route is not wired; host ownership and the
bridge contract remain to be verified. The root kernel never imports MOSAIC.
MOSAIC consumes evidence references and
returns advisory `PromotionCandidate`, `Hold` or `Revise` recommendations.
It cannot dispatch experiments, mutate proposal state, or promote a method.

## Boundaries

- Brain coordinates typed reasoning stages and returns a policy decision; an execution plan and plan-validation report are optional and appear only when `ExecutionDesign` produces a plan. Fast and Simple Adaptive runs return stage records and a decision without a plan or plan-validation report. Adaptive is the default mode and selects Fast, Standard or Deep depth from the intent-stage complexity assessment; explicit modes remain available.
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