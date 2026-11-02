# Lean ⇔ Fleet Notation Mapping — Matrices & Vector Stores

**Record of the notation-mapping leg** (Linguist lane, 2026-11-02; owner
directive "Notations Matrices && other Utilization"). Per class:
{fleet symbol/term ⇔ Lean/Mathlib notation · grade exact | ≈ · ker named
where the crosswalk is lossy}. Gaps and conflicts are named, not smoothed.

**Consumers:** (1) this Matrices record; (2) NSE-023 — this table is the
first input class for proposition shapes (`research/nse-023/`).

## Surface keying (census-confirmed ONLY)

| Surface | Status (census 2026-11-02) |
|---|---|
| operator-matrix (issues/PRs × families) | LIVE-generated |
| lane-matrix (lane-matrix-status / sweep v2) | LIVE-generated |
| domain-composition matrix (seed) | in-repo crosswalk table |
| nomenclature equivalency matrix + seed | in-repo crosswalk table (incl. group_theory layer) |
| Pinecone (pinecone-knowledge) | LIVE — the only real vector store |
| pgvector | docs-only mentions; 0 `vector(n)` columns; Neon enablement NOT_ESTABLISHED |
| sqlite-vec | ABSENT |
| archwiz/graph_tensors (.npz) | graph tensors — ¬ an embedding store |
| Lean code in tree | ∅ `.lean` / lakefile; Batteries pin `36cc05ca` only |
| Mathlib | NOT a landed surface — mapping rows are spec-level until a pinned Mathlib dependency lands (owner ruling 2026-11-02: Mathlib IN for the Lean Implementation, as pinned dependency {pin · license · provenance}) |

## Class 1 — MATRICES

| fleet term/symbol | Lean/Mathlib notation | grade | ker (named loss) |
|---|---|---|---|
| operator-matrix: incidence of issues/PRs × families | `Matrix m n ℕ` (or `Bool`) over index types = the two sets | ≈ | fleet cells are generated classifications w/ provenance; Lean entries are bare counts. ker = classification provenance |
| lane-matrix: lanes × scopes/status grid | `Matrix m n α` with α = status type | ≈ | status is an enum/record, not a scalar; ker = cell payload (links, states) beyond the entry value |
| crosswalk table (nomenclature/domain-composition): relation-valued cells | `Matrix m n α` | ≈ | **the central ker:** cells carry relation + confidence + evidence (SKOS-style); Lean entries are pure values. ker = relation semantics + confidence + provenance |
| cell access `M[i,j]` | `M i j` (Matrix is `m → n → α`, application) | exact | — |
| literal finite table | `!![a, b; c, d]` (from `![![…], ![…]]`) | ≈ | fixes index types `Fin m × Fin n`; fleet keys are strings |
| vector literal | `![a, b, c] : Fin n → α` | exact | — |
| `∘` composition (fleet (G, ∘) frame) | matrix `*` (`Matrix.mul`, Σ over middle index) | ≈ | ker = the Σ + ring structure (`Fintype`, `AddCommMonoid`) — fleet ∘ has no summation |
| `e` = ∅-op (group_theory layer) | `1 : Matrix n n α` (diagonal of 1s) | exact (monoid identity) | square matrices under `*` form a monoid, ¬ a group; units only = `GL(n, α)`. ker = singular matrices |
| non-abelian default | matrix `*` is non-commutative | exact | — (fleet default carries over 1:1) |
| `≅` (proof-gated; else `≈`) | Lean proof term discharges the claim (NSE-023 oracle) | exact | Lean is the fleet's proof oracle for ≅ claims |
| transpose | `Mᵀ` (`Matrix.transpose`) | — | GAP fleet-side: no transpose symbol in the fleet spec |
| notation/label registry (seed.json) | `notation` / `infixl` declarations (scoped syntax + precedence) | ≈ | fleet labels are data records; Lean notation is syntax machinery. Function-level correspondence only |

**Conflict (named):** fleet "Matrix" (crosswalk/ops tables) vs Mathlib
`Matrix m n α` is a homonym — in matrix vocabulary, `ambiguous_with`.
Never read as exact; every row above is graded accordingly.

**Proposition supply (→ NSE-023):** P-001 ∘-associativity = PASS
(run 41457244573). Next exact rows admissible as propositions: cell-access
and vector-literal identities (core/Batteries level); `e`↦`1` and
non-abelian rows become propositions only with a Mathlib pin (their
statements need `Matrix`).

## Class 2 — VECTOR STORES

| store/fleet term | Lean/Mathlib notation | grade | ker |
|---|---|---|---|
| vector / embedding | `Fin n → ℝ`; `EuclideanSpace ℝ (Fin n)`; literal `![…]` | ≈ | ker = embedding **model** (unnamed parameter) + float32 precision + normalization |
| cosine similarity (Pinecone query) | `⟪x, y⟫ / (‖x‖ ‖y‖)` (InnerProductSpace) | exact (formula) | — |
| ANN top-k search | — (exact argmax over a `Finset` is definable only) | — | GAP Lean-side: no ANN in Mathlib; ker = recall < 1 |
| upsert (Pinecone records/namespaces) | `Function.update f i v` | ≈ | pointwise-update analog is exact for finite functions; the store op is effectful/remote |
| namespace | subtype `{x // p x}` / index-set partition | ≈ | loose |
| metadata filter | `Finset.filter p`; predicate subtypes | ≈ | — |
| record {id, values, metadata} | Σ-type / structure — definable, no standard Mathlib type | — | GAP: no named counterpart |
| the index/store itself | — | — | GAP Lean-side: persistence/effects are outside Mathlib scope |
| pgvector `vector(n)` column | (same vector rows as above) | ≈ | surface itself docs-only ⇒ rows keyed NOT_ESTABLISHED for this surface |
| sqlite-vec | — | — | ABSENT surface — no crosswalk asserted |

**Boundary (named):** the crosswalk terminates at the vector *object*.
Lean owns the math (inner product, `1`, `GL`, proof-gated `≅`); stores own
the systems (upsert, ANN, persistence). Neither side's terms substitute
for the other's.
