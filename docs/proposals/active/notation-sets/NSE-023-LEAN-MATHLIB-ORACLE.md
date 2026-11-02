# NSE-023 — LEAN / Mathlib constraint oracle starting at `batteries_fork`

## Intent

Define the research entry point for a **constraint oracle**: machine-checked propositions, lemmas, and tactics that can later bound Grimoire IR (NSE-015) and notation taxonomy (NSE-021).

## Submodule reality (tree gap → document absence)

| Fact | Evidence |
|------|----------|
| Submodule declared | `.gitmodules` → `refTemplates/smods/batteries_fork` |
| Fork | `timerloggedout-spec/batteries_fork` (source: leanprover-community/batteries) |
| Pinned revision | `36cc05ca2d0e469bfbeea9437f460e19238e885e` |
| Role | Lean 4 extended-library foundation / experimental dependency |
| Docs | `docs/submodules/batteries_fork.md`, `docs/submodules/batteries-preproofing.md`, `docs/submodules/fork-inventory.yaml` |
| Full Lean tree in monorepo search | **Absent** (shallow pin; research-first placement) |

**Tree gap rule:** absence of searchable Lean sources under the monorepo root is expected until a deliberate research packet is compiled against the pin. Document the gap; do not invent Mathlib coverage.

## Pre-proofing lane (from batteries-preproofing)

1. State proposition shape.
2. Normalize goal (types, decidability, structure).
3. Prefetch candidates from pinned Batteries + recorded upstream revision.
4. Record provenance (name, path, revision, toolchain, import, license).
5. Adapter lemma if close-but-not-exact; never counterfeit authorship.
6. Compile smallest example against pin.
7. Generalize only after success.
8. Promote only with stable dependency contract.

## Oracle contract (specification)

- Input: normalized IR fragment or notation claim (NSE-015 / NSE-021).
- Output: `PASS | FAIL | INCONCLUSIVE` + provenance + pin revision.
- Fail-closed when import/toolchain cannot be reproduced.
- Never treat HTTP 200 / workflow success as mathematical PASS.

## Relationship to Mathlib

Mathlib is the broader machine-checked library. This extract starts at **Batteries** (foundation) only. Any Mathlib surface requires a separate, pinned, licensed dependency decision and dual-gate review.

## Status

**LAUNCHED — research-active** (owner word, 2026-11-02, relayed via main). The research lane is open under this proposal's own governance: the pre-proofing lane and the oracle contract above are in force, fail-closed. First research packet: `research/nse-023/` (input class 1 = the Linguist matrices/vector-stores ⇔ Lean notation mapping; first proposition P-001, composition associativity). **Mathlib stays OUT** — a separate pinned/licensed dependency decision with dual-gate review is required before any Mathlib surface; this launch does not authorize it.
