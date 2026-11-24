# Rust migration tooling — DoE candidate

**State:** proposed / not admitted. This directory records a pre-registration candidate; it contains no run results and makes no performance claim.

## Candidate implementations

| Arm | Pinned source | Current crate version | Intended scope |
|---|---|---:|---|
| Native baseline | Python fixture corpus | — | Unmodified behavior and runtime |
| fast-anything | [fork](https://github.com/timerloggedout-spec/fast-anything_fork) @ `80ab099817b3d07ebe5b5221d4a9c6b881cfd044` | `0.8.0` | Reversible selective hot-path port |
| rust-anything | [fork](https://github.com/timerloggedout-spec/rust-anything_fork) @ `50d3810b622fdc6cb3aee965fe4c9d4b4f29205b` | `3.3.0` | Selective hot-path port in the primary comparison; whole-app migration is a separate study |

The two tools share a hot-path `go` use case, while rust-anything exposes a broader piecewise whole-app migration path. The primary experiment compares only their common hot-path scope.

## Extensible task contract

Each workload fixture conforms to [TASK.schema.json](TASK.schema.json). Add workloads through versioned fixture records with source hashes, baseline/candidate commands, held-out oracle references and explicit observable behavior. New tasks create a new cohort/design version; prior records remain immutable.

## Development-process note — GitReverse

Use [filiksyos/gitreverse](https://github.com/filiksyos/gitreverse) as a process reference for the ongoing development work in `termux-monorepo`. Its approach will inform a further Rust.rs implementation/version, initially developed in this Rust migration lane. This is a development note, not a separate DoE campaign or comparison treatment. Admit the new Rust version as a treatment only after pinning its source revision, capability contract, integration boundary, Siglary profile where applicable, and fixture compatibility. Preserve the upstream MIT notice when reusing covered material.

## Design

See [DESIGN.json](DESIGN.json). The planned design is a blocked full factorial with one three-level treatment factor, six frozen Python workloads, three repetitions, and 54 planned observations. Treatment order is randomized within each task × repetition block.

The primary decision is quality-constrained: each tool must pass the same independent held-out behavioral suite before runtime gains are considered. Report whole-application and per-call timing separately. Record failures, missing measurements, compilation, memory, tool/agent effort, and integration burden.

## Future Rust implementation extension

The GitReverse approach is a development-process reference for work happening in `termux-monorepo`. The next Rust.rs implementation/version is developed initially in this existing migration lane. GitReverse is not a sibling campaign, comparison arm, or research-seed entry.

A future implementation enters a new design version only after its source commit, capability contract, integration boundary, Siglary profile where applicable, and fixture compatibility are pinned. Keep reconstruction-quality outcomes separate from the Rust hot-path performance cohort.

## Execution status

- Source repositories and candidate commits: pinned.
- Crate versions: read from each fork's `Cargo.toml`.
- Common language/runtime and primary scope: specified.
- Fixture corpus, runner image digest, configured agent identity, automation, and run records: pending.
- Admission: blocked pending the gates in `DESIGN.json`.

## Method boundaries

Recorded-call replay is evidence bounded by the calls and edge cases exercised; it is not a proof of all possible behavior. The independent held-out corpus provides a common cross-tool correctness check. Whole-app side-effect fidelity is a separate rust-anything capability and must not be used to inflate the primary hot-path comparison.

The campaign uses the existing DoE family, canonical experiment record schema, and GitHub Actions execution surfaces. It creates no parallel scheduler or result ledger.
