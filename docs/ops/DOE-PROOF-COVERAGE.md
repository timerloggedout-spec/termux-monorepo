# Proof coverage map — MOVED (pointer)

The coverage map of record now lives in the proofs directory
of record as its index, per the owner amendment of 2026-11-03
(proofs get a directory, wired to the data layers):

- **Index (the map):** `experiments/doe/proofs/INDEX.md`
- **Wiring manifest:** `experiments/doe/proofs/MANIFEST.json`
  — every entry: {experiment · proof citation + provenance ·
  oracle run · verdict · DATA LAYERS (named refs) · status}.
- **Artifacts** stay in the Lean home
  (`research/nse-023/examples/`) and enter the directory by
  citation — no silent moves, this pointer included.

The full map text as landed by PR #4733 is preserved verbatim
in the directory's INDEX. An entry missing its proof OR its
data-layer refs reads INCOMPLETE.
