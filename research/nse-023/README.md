# research/nse-023 — Lean/Batteries constraint-oracle research lane

Governed by `docs/proposals/active/notation-sets/NSE-023-LEAN-MATHLIB-ORACLE.md`
(LAUNCHED — research-active, owner word 2026-11-02). This directory is the
governed `research/` path the proposal requires before any applied promotion.

## Rules of the lane

- **Pin:** Batteries fork `timerloggedout-spec/batteries_fork` @
  `36cc05ca2d0e469bfbeea9437f460e19238e885e` (submodule
  `refTemplates/smods/batteries_fork`), toolchain `leanprover/lean4:v4.34.0-rc1`
  (the pin's own `lean-toolchain`). No other revision is an oracle input.
- **Pinned dependencies only.** Batteries ∧ Mathlib ∧ further libraries
  are IN scope (owner ruling 2026-11-02) — each ONLY as a pinned dependency
  recorded in [DEPENDENCIES.md](DEPENDENCIES.md) {pin revision · toolchain ·
  license · provenance}, under dual-gate review. An unpinned or unrecorded
  library is not an oracle input. Each dependency compiles under its OWN
  pinned toolchain.
- **Oracle contract (fail-closed):** every proposition run emits
  `PASS | FAIL | INCONCLUSIVE` + provenance + pin revision. A green workflow
  alone is never a PASS — PASS requires the Lean kernel to have accepted the
  proof (compiler exit 0, no errors, axioms printed and recorded).
  Toolchain/import reproduction failure ⇒ INCONCLUSIVE, never PASS.
- **Pre-proofing lane (per packet):** (1) state proposition shape →
  (2) normalize (types, decidability, structure) → (3) prefetch candidates
  from the pinned Batteries → (4) record provenance (name, path, revision,
  toolchain, import, license) → (5) adapter lemma if close-but-not-exact;
  never counterfeit authorship → (6) compile the smallest example against
  the pin via `.github/workflows/nse023-oracle.yml` → (7) generalize only
  after success → (8) promote only with a stable dependency contract.

## Input classes

1. **Linguist notation mapping** — landed record:
   `docs/proposals/active/notation-sets/LEAN-NOTATION-MAPPING.md`
   (matrices · vector stores ⇔ Lean/Mathlib notation, keyed to
   census-confirmed surfaces only): the exact/≈-qualified rows are
   the proposition supply. Mathlib-side rows stay NOT_ESTABLISHED — they are
   not oracle inputs until Mathlib is separately admitted. Batteries/core
   rows (composition, function-level claims) are admissible now.
2. NSE-021 taxonomy claims as they are formalized into proposition shapes.

## Packets

| Packet | Proposition (fleet claim) | Verdict |
|---|---|---|
| [P-001](packets/P-001.md) | ∘ is associative — the (G, ∘) frame axiom | **PASS** (run 41457244573; axioms [Quot.sound]) |
| [P-002](packets/P-002.md) | `e` ↦ `1`: matrix identity (`1 * M = M`) — first Mathlib packet | PENDING (Mathlib leg) |
