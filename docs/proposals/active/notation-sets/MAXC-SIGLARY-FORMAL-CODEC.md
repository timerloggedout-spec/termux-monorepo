# MAXC × Siglary — Formal Semantic Codec Architecture

**Work item:** NSE-020  
**Status:** proposed design / implementation scope  
**Authority:** `docs/proposals/active/notation-sets/ITEMS.md`  
**Canonical notation:** Siglary Standard + Notation Matrice  
**Principle:** accuracy > compression; canonical IR > rendered shorthand.

## Outcome

Evolve MAXC from a markup-oriented compiler into a multi-target, semantics-preserving codec for Siglary and structured agent communication. MAXC parses source surfaces into a typed canonical intermediate representation (IR), applies deterministic reductions, verifies eligible rewrite laws, measures target-specific cost, and emits reversible target representations.

MAXC remains a compiler/codec. It does not become the policy authority, planner, proof assistant, or execution engine.

## Repository baseline (master, 2026-11-13)

- `workspace/maxc/` contains a Rust compiler with HTML, Leptos, and micro-bytecode emitters.
- `appliedSxi/maxc/` contains a second Cargo package also named `maxc`, with an older/smaller implementation.
- Both Cargo manifests identify package `maxc`; the repository already flags the duplicate as a consolidation question.
- `workspace/maxc/src/emitter_micro.rs` emits `MAXC` version-1 bytecode with LEB128 lengths and compact token IDs.
- The current AST is markup-oriented (`Element` / `Text`), not a typed logical-expression IR.
- Siglary already has a canonical Matrice, a token-cost study, a Lean/Mathlib crosswalk, and a candidate PDDL worked example.
- The Lean crosswalk records a Batteries pin and a Mathlib pin; it also records that no `.lean` source or Lake project existed at the time of its census.

This design preserves both MAXC histories pending a source/consumer/CI inventory. It does not silently select, delete, rename, or merge either crate.

## Baseline risks requiring a parser-hardening pass

The current `workspace/maxc/src/parser.rs` has two behaviors that are incompatible with a semantics-preserving compiler contract:

- It writes `parse_debug.log` during parsing, creating an unconditional filesystem side effect.
- It advances past `Unknown` tokens without a structured diagnostic or preserved unknown-node representation.

Before enabling semantic optimization, make parsing pure and observable: return structured diagnostics with source spans; preserve unknown syntax as an explicit opaque node where safe; fail closed when an unknown token could change meaning; keep debug output behind an explicit CLI flag. Add regression tests for unknown tokens, malformed input, no filesystem writes, and deterministic parse output.

The markup parser and the new logical/Siglary parser should remain distinct frontends over the shared IR. Do not reinterpret MaxUp tokens as Siglary operators based on visual similarity.

## Target architecture

```text
Siglary / MaxUp / Markdown / JSON / PDDL summaries
                    |
                    v
             Frontends + parsers
                    |
                    v
          Typed canonical semantic IR
          (scope, domain, type, provenance)
                    |
                    v
        Deterministic normalization passes
                    |
           +--------+---------+
           |                  |
           v                  v
      Cost model         Proof obligations
           |                  |
           |             Lean 4 / Batteries
           |             Mathlib where needed
           |                  |
           +--------+---------+
                    |
                    v
        Candidate selection / e-graph
                    |
                    v
         Round-trip + contract validation
                    |
                    v
     Markdown / HTML / JSON / CBOR / MAXC
       Siglary A2A / display / PDDL adapter
```

The IR is truth-bearing. Every emitted compact form is a versioned projection with a decoder and an explicit semantic-loss report.

## Semantic IR

Minimum expression algebra:

- `Atom(id, domain, type, provenance)`
- `Not(expr)`
- `And(expr[])`
- `Or(expr[])`
- `Implies(lhs, rhs)`
- `Equivalent(lhs, rhs, register, proof_ref?)`
- `ForAll(variable, domain, expr)`
- `Exists(variable, domain, expr)`
- `SetMember(value, set)`
- `StateTransition(preconditions, effects)`
- `Action(name, parameters, preconditions, effects)`
- `Reference(semantic_id, codebook_version)`

Every node carries source spans and a domain/register tag. Siglary's three classes remain distinct: GLYPHS, CHORDS, OPERATORS. Chord resolution requires a named Shorthand Domain. The chat-only `N∅` marker never enters persisted IR or data-of-record; unknown facts use schema nulls and typed epistemic status.

## MAXC reduction passes

| Pass | Rule | Safety condition |
|---|---|---|
| R0 | Exact duplicate elimination | Identical typed node + scope |
| R1 | Associative flattening | Same operator and compatible types |
| R2 | Idempotence | `A ∧ A → A`, `A ∨ A → A` |
| R3 | Common-subexpression interning | Stable semantic ID + same scope |
| R4 | Predicate factoring | Quantifier/domain/scope preserved |
| R5 | Alias canonicalization | Registry marks alias as exact in this domain |
| R6 | Equality-saturation extraction | Only equivalence-class members with valid rewrite provenance |
| R7 | Dictionary/codebook substitution | Receiver has exact codebook version and decoder |

Never apply commutativity to order-sensitive constructs, distribution across quantifiers without side conditions, implication/equivalence rewrites across registers, or a cross-domain analogue as if it were exact. Unknown or ambiguous expressions remain expanded.

### Example

Input:

```text
∀a∈Agents: ¬fluff
∀a∈Agents: ¬repetition
∀a∈Agents: ¬ceremony
∀a∈Agents: ¬fluff
```

Candidate normalized form:

```text
∀a∈Agents: ¬(fluff ∨ repetition ∨ ceremony)
```

The optimizer may emit this only after confirming the shared quantifier, domain, variable binding, and interpretation of the predicates. It records the source-to-IR map and the rewrite sequence.

## LEAN 4 + Batteries proof lane

Use Lean as the proof oracle for the algebraic rewrite kernel, not as the runtime parser or planner.

Initial theorem cohort:

1. conjunction/disjunction associativity and commutativity under their normal logical semantics;
2. idempotence;
3. De Morgan laws;
4. double negation;
5. implication normalization;
6. safe factoring identities;
7. list/set deduplication laws with explicit equality assumptions;
8. preservation of bound-variable scope for quantifier transformations.

Batteries supplies supporting data structures, tactics, and utilities where useful. Mathlib supplies broader mathematical results when required. Pin dependencies and record the exact Lean toolchain, package revisions, theorem source, build command, and proof artifact hash.

Rust may apply a rewrite marked `PROVEN` only when its rule ID and version map to a successful proof artifact. `TESTED`, `HEURISTIC`, `CANDIDATE`, and `UNPROVEN` remain distinct states. Property tests supplement proofs; they do not upgrade heuristic transformations to proven.

## PDDL planning adapter

PDDL remains the planning/control language. MAXC may parse and summarize PDDL into the IR, emit Siglary reading stamps, and preserve a pointer to the authoritative `.pddl` source.

- PDDL syntax stays pure PDDL; Siglary glyphs/chords belong in comments, summaries, or display stamps.
- PDDL planner output is a candidate plan, not execution evidence.
- Runtime authorization and precondition checks remain at the execution boundary.
- Preserve types, requirements, negative preconditions, action effects, and planner identity in the IR. A compact summary must disclose omitted detail and link to the source problem/domain.

The existing `PDDL-SIGLARY-EXAMPLE.md` remains candidate material until its planner-validation and Linguist review gates are satisfied.

## Cost model and target selection

Optimize the actual delivery objective, not character count:

```text
cost(rendering) =
  α·target_tokens
+ β·decode_risk
+ γ·ambiguity
+ δ·round_trip_cost
+ ε·latency
+ ζ·bytes
```

Hard constraints: semantic recovery = pass; output contract = pass; task-quality floor = pass; codebook available = true. Minimize cost only within the valid candidate set.

Measure per tokenizer/model and per register. The current Siglary A2A evidence favors OPERATORS + plain one-token words over CHORDS + GLYPHS for machine payloads; display register may still select visual forms. Re-measure on tokenizer or Matrice changes.

## Output formats

| Target | Role |
|---|---|
| `.md` | Human-reviewable canonical source, diffs, and receipts |
| `.html` | Human display, dashboards, documentation projection |
| `.json` | Debuggable, interoperable semantic IR |
| `.cbor` | Compact typed machine interchange |
| `.maxc` | Versioned binary AST/IR transport |
| `.pddl` | Planning-domain/problem output only through a validated adapter |
| `A2A` | Context-bound message rendering with receiver-compatible codebook |

Markdown and HTML are complementary outputs, not competing canonical stores. JSON is the inspectable interchange surface; CBOR/MAXC are compact machine surfaces. The canonical IR and source provenance remain recoverable from each artifact's receipt.

## Formal-methods portfolio

| Technology | MAXC/Siglary responsibility | Adoption |
|---|---|---|
| Lean 4 + Batteries | Prove rewrite-kernel laws | P0 |
| Mathlib | Extended algebra and structures | P0 when theorem needs it |
| PDDL | Action planning and state-space search | Existing candidate; validate |
| SMT/Z3 | Numeric/resource constraints and satisfiability | P0 adapter |
| JSON Schema | IR, receipt, and codebook contracts | P0 |
| TLA+ | Concurrency, lease, retry, and state invariants | P1 |
| Tree-sitter | Source-language structural extraction | P1 |
| e-graphs (`egg`) | Equality saturation and cost-based extraction | P1 |
| OPA/Rego | Runtime policy enforcement | P1 |
| Temporal logic | Always/eventually/until/deadline properties | P1 |
| RDF/SHACL | Semantic graph interchange and shape validation | P2 |

These tools retain separate authority boundaries. A planner proposes; a solver answers its encoded constraint problem; Lean proves theorem statements; OPA evaluates policy; runtime evidence establishes execution.

## Compatibility and migration

1. Inventory both MAXC crates, consumers, workflows, lockfiles, generated artifacts, and import paths.
2. Designate the canonical crate only after evidence-backed comparison; retain a compatibility facade or migration note for the other.
3. Preserve existing HTML, Leptos, and micro-bytecode behavior with golden fixtures.
4. Add the semantic IR as a new module/crate boundary; avoid destabilizing the markup AST.
5. Introduce new bytecode only under a new format version or explicit feature flag. Keep the version-1 decoder stable.
6. Add Markdown and HTML as distinct emitters from the same IR.
7. Add Lean proofs and Rust property/round-trip tests before enabling optimizer passes by default.

## Acceptance and evidence

- [ ] NSE-020 accepted in the proposal lifecycle.
- [ ] Duplicate MAXC crate inventory and canonical ownership decision recorded.
- [ ] Typed IR schema and versioned codebook contract reviewed.
- [ ] Each rewrite has a domain, side conditions, rule ID, and test.
- [ ] Proof-gated rules link to reproducible Lean artifacts.
- [ ] Round-trip tests recover equivalent canonical IR.
- [ ] A2A token-cost benchmarks use the target tokenizer and matched semantic payloads.
- [ ] Quality, ambiguity, latency, token count, byte count, and repair rate are reported together.
- [ ] HTML/Leptos/micro v1 golden fixtures remain compatible.
- [ ] PDDL examples are planner-checked and source-linked.
- [ ] `repo-gate` and `termux-smoke` pass on the implementation branch.

## Explicit boundaries

This design adds no new Siglary glyphs or chords by implication. It does not make visual brevity a token-saving claim, convert candidates into canonical mappings, treat a planner plan as authorization, or label a rewrite proven without a pinned proof artifact. No MAXC crate is deleted or consolidated in this documentation slice.
