# Context Relationship Rust Accelerator

This is an **optional hot path**, not a second source of truth.

## Contract

- Input: newline-delimited JSON fragments on stdin.
- Output: one JSON analysis object on stdout.
- Full BLAKE3-256 is retained for identity verification.
- Human/editable refs use a 128-bit truncated digest encoded as 22 base64url characters.
- A truncated ref is never treated as collision-proof by itself; the full digest remains canonical.
- Zipf alpha is diagnostic evidence only. Pointer selection uses observed frequency and an explicit byte-cost model.
- No source text is persisted by the accelerator beyond the process input/output boundary.

## Why this shape

The existing Python Context Relationship compiler remains authoritative for schema validation, evidence classification, privacy boundaries, and canonical artifacts. Rust is used where a tight loop benefits from native execution: fingerprinting, frequency accounting, and cost estimation.

The same boundary can later host other implementations (for example a Python reference implementation, a C/Rust parser adapter, or a WASI worker) without changing the graph schema.
