# Rust migration tooling — DoE candidate

**State:** proposed / not admitted. This directory records a pre-registration candidate; it contains no run results and makes no performance claim.

## Candidate implementations

| Arm | Pinned source | Current crate version | Intended scope |
|---|---|---:|---|
| Native baseline | Python fixture corpus | — | Unmodified behavior and runtime |
| fast-anything | [fork](https://github.com/timerloggedout-spec/fast-anything_fork) @ `80ab099817b3d07ebe5b5221d4a9c6b881cfd044` | `0.8.0` | Reversible selective hot-path port |
| rust-anything | [fork](https://github.com/timerloggedout-spec/rust-anything_fork) @ `50d3810b622fdc6cb3aee965fe4c9d4b4f29205b` | `3.3.0` | Selective hot-path port in the primary comparison; whole-app migration is a separate study |

The two tools share a hot-path `go` use case, while rust-anything exposes a broader piecewise whole-app migration path. The primary experiment compares only their common hot-path scope.

## Design

See [DESIGN.json](DESIGN.json). The planned design is a blocked full factorial with one three-level treatment factor, six frozen Python workloads, three repetitions, and 54 planned observations. Treatment order is randomized within each task × repetition block.

The primary decision is quality-constrained: each tool must pass the same independent held-out behavioral suite before runtime gains are considered. Report whole-application and per-call timing separately. Record failures, missing measurements, compilation, memory, tool/agent effort, and integration burden.

## Extensible comparison track

GitReverse is registered as a sibling capability campaign in `DESIGN.json`, with upstream `filiksyos/gitreverse`, the in-progress internal implementation, and a structured human-reference baseline. Its reconstruction-quality outcomes remain separate from Rust hot-path speed outcomes.

The Siglary relationship is recorded as an explicit source-recon gate. The campaign freezes Siglary-on/off as a factor only if the internal implementation supports a stable switch on one source revision; otherwise Siglary use is a treatment attribute or a separate cohort. The internal implementation's exact path, commit and Siglary version remain pending source verification.

## Execution status

- Source repositories and candidate commits: pinned.
- Crate versions: read from each fork's `Cargo.toml`.
- Common language/runtime and primary scope: specified.
- Fixture corpus, runner image digest, configured agent identity, automation, and run records: pending.
- Admission: blocked pending the gates in `DESIGN.json`.

## Method boundaries

Recorded-call replay is evidence bounded by the calls and edge cases exercised; it is not a proof of all possible behavior. The independent held-out corpus provides a common cross-tool correctness check. Whole-app side-effect fidelity is a separate rust-anything capability and must not be used to inflate the primary hot-path comparison.

The campaign uses the existing DoE family, canonical experiment record schema, and GitHub Actions execution surfaces. It creates no parallel scheduler or result ledger.
