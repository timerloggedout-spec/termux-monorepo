# Context Relationship Polyglot Acceleration

Status: implemented on `feat/context-relationship-rust-acceleration`.

## Decision

The repository keeps **one canonical graph contract** and allows multiple execution languages behind it:

```text
                         canonical CRG schema
                                │
                 ┌──────────────┴──────────────┐
                 │                             │
          Python reference path          optional hot paths
                 │                             │
       AST / GitHub / validation       Rust fingerprint engine
                 │                             │
                 └──────────────┬──────────────┘
                                ▼
                   metadata-only graph records
                                │
                         L1 / L2 corpus
```

Python remains authoritative for:

- repository/scope boundaries;
- Python AST semantics and parser coverage;
- GitHub collection;
- evidence classification;
- privacy and sensitive-path rejection;
- schema validation and canonical artifact publication.

Rust is optional and owns only CPU-dense, deterministic operations:

- BLAKE3-256 fragment fingerprinting;
- compact 128-bit human/editable reference derivation;
- frequency accounting;
- byte-cost pointer decisions;
- Zipf alpha as an observational statistic.

This avoids a second graph implementation and makes acceleration independently replaceable.

## Pointer identity

The collaborator's original 48-bit reference was rejected as a canonical identity. At one million objects its birthday-collision probability is about **0.177%**.

The implemented format therefore keeps:

- **BLAKE3-256** as the canonical full digest;
- **128-bit truncated digest** for compact `@<...>` references;
- **22 base64url characters** for the compact reference;
- full digest verification whenever a compact reference is resolved.

The compact reference is an address, not proof of uniqueness.

## Policy

Zipf alpha is **measurement**, not a hard enable/disable gate.

Pointer selection is based on observed corpus frequency and an explicit storage model:

```text
estimated_savings =
    (frequency - 1) * fragment_bytes
  - frequency * reference_bytes
  - node_overhead
```

A fragment is eligible only when:

- frequency >= 2;
- fragment bytes >= configured minimum;
- estimated savings > 0.

This prevents a statistical fit from overriding the actual storage economics.

## Source fidelity

Do not normalize source by naive comment stripping. Python strings, comments, multiline literals, and language-specific lexical rules make that unsafe.

The accelerator fingerprints the **exact accepted source bytes**. Any semantic normalization belongs in a language-specific parser/provider and must remain an explicit, versioned measurement rather than silently changing source identity.

## Language modularization

The execution boundary is JSONL over stdin/stdout and is intentionally language-neutral:

```text
Python AST provider ─┐
Tree-sitter provider ├──> normalized fragment records ──> Rust hot path
C/C++ provider ──────┤
other language tool ─┘
```

A future provider may be implemented in Python, Rust, C/C++, Go, Zig, or another controlled executable without changing the CRG schema.

Providers must:

1. accept only bounded, repository-approved inputs;
2. emit metadata records, never secrets or session material;
3. preserve source-path and parser-coverage provenance;
4. never become an autonomous GitHub write authority.

## Termux operating model

The accelerator is deliberately **optional**.

```sh
cargo build --release --manifest-path archwiz/context_relationships/rust_accel/Cargo.toml
CRG_RUST_ACCEL=required \
CRG_RUST_ACCEL_BIN=archwiz/context_relationships/rust_accel/target/release/crg-rust-accel \
python -m archwiz.context_relationships.source_collector ...
```

Without the binary, the Python reference path continues unchanged.

For production CI, the existing context-relationship validation workflow compiles and tests the accelerator. Its existing graph path trigger admits the Rust lane without creating a second validation surface.

## Rejected designs

- Raw pointers in serialized graph records.
- 48-bit-only object identity.
- Unicode graphemes as node IDs: UTF-8 width, normalization, confusables, and grapheme segmentation make this inferior to a binary/encoded digest.
- A mandatory Zipf threshold.
- Whole-file compression as the graph identity.
- Replacing the existing metadata-only graph with a new Rust datastore.
- Naive language-independent source normalization.

## Acceptance invariants

1. Python collector output remains schema-compatible with the current CRG compiler.
2. Accelerator absence is a clean no-op in default/auto mode.
3. Required accelerator failure is explicit and fails closed.
4. Full digest is retained for collision verification.
5. Compact refs are stable for identical content.
6. Pointer policy is justified by observed frequency and cost.
7. Existing verified/candidate graph semantics remain unchanged.
8. No source text is written to canonical graph artifacts by the accelerator.
