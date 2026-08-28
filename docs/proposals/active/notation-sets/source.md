# Source — Notation Sets, Living Lexicon, and Cross-Domain Semantic Index

## 1. Why this proposal exists

Issue #320, **Notation Sets**, supplies a cross-domain notation seed and explicitly connects itself to #309/#182 plus additional issue maps. The proposal treats that material as the beginning of a vocabulary specification rather than as a finished implementation.

The key architectural recommendation is:

```text
#320 Notation Sets
      │
      │ canonical vocabulary + semantic distinctions
      ▼
#309 / #182 Grimoire compression
      │
      │ compact representation with reversible semantics
      ▼
repository indexes / context relationships / automation
```

The repository already contains several index families, including `archwiz/CONCEPT_INDEX.md`, `archwiz/POINTER_INDEX.md`, `archwiz/TOOL_INDEX.md`, `archwiz/METHODOLOGY_INDEX.md`, `workspace/llm_map/ALIAS_INDEX.md`, `workspace/llm_map/INDEX_OVERVIEW.md`, and the ICM context-relationship index. These should be composed rather than replaced.

## 2. Notation research seed from #320

#320 identifies core category-theoretic structures and maps parallel notation across category theory, set theory, formal logic, type theory / functional programming, and order theory (posets).

### 2.1 Core Category Theory Notation

A category $\mathcal{C}$ consists of a collection of objects ($A, B, C$) and morphisms (arrows) between them:

- **Morphism Assignment:** $f: A \to B$ (arrow with domain/source $A$ and codomain/target $B$).
- **Composition:** $g \circ f$ or $g f$ (if $f: A \to B$ and $g: B \to C$, then $g \circ f: A \to C$; read "g after f").
- **Diagrammatic Composition:** $f ; g$ or $f \gg= g$ (read "f then g"; left-to-right ordering).
- **Hom-Set:** $\text{Hom}_{\mathcal{C}}(A, B)$ or $\mathcal{C}(A, B)$ (collection of all arrows pointing from $A$ to $B$).
- **Identity:** $\text{id}_A$ or $1_A$ (mandatory arrow mapping an object to itself without modification).
- **Functor:** $F: \mathcal{C} \to \mathcal{D}$ (structure-preserving map between categories transforming objects and morphisms).
- **Natural Transformation:** $\alpha: F \implies G$ (mapping between functors providing a bridge between structural paths).

### 2.2 Advanced & Dual Notations

- **Opposite Category ($\mathcal{C}^{\text{op}}$):** Same category with all arrows reversed.
- **The "Co-" Prefix / Duals:** Structural dual achieved by reversing arrows (e.g., Products $\times$ dualize to Coproducts $\sqcup$ or $+$, Limits dualize to Colimits).
- **Exponential Objects ($Y^X$):** Internal object of arrows from $X$ to $Y$, structurally matching the set-theoretic total functions $|Y|^{|X|}$.

### 2.3 Cross-Domain Notation Mapping Table

| Framework | Arrow / Mapping Notation | Composition Notation | Identity Concept |
|---|---|---|---|
| **Category Theory** | $f: A \to B$ | $g \circ f$ (or $f ; g$) | $\text{id}_A$ |
| **Set Theory** | $f: X \to Y$ (Functions) | $(g \circ f)(x) = g(f(x))$ | $I(x) = x$ |
| **Formal Logic** | $A \implies B$ (Implication) | If $A \implies B$ and $B \implies C$, then $A \implies C$ (Hypothetical Syllogism) | $A \implies A$ (Tautology) |
| **Type Theory & FP** | $f :: A \to B$ (Types) | $g . f$ (or $f >>> g$) | $id$ |
| **Order Theory (Posets)** | $x \le y$ (Relations) | If $x \le y$ and $y \le z$, then $x \le z$ (Transitivity) | $x \le x$ (Reflexivity) |

The important research constraint is **semantic non-collapse**. Similar glyphs or analogous relationships across fields do not automatically imply identical semantics. The index therefore records both the shared structural relation and the domain boundary.

## 3. Living lexicon / dictionary model

The proposal interprets the user's "index glossary dictions{?}" as a **living index + glossary + dictionary layer**:

- **Index:** where a concept/symbol occurs in the repository.
- **Glossary:** what the concept/symbol means in a stated domain.
- **Dictionary:** normalized keys, aliases, variants, relations, and lifecycle metadata that permit deterministic lookup and transformation.

A conceptual record should be shaped approximately as:

```yaml
key: category_theory.composition
symbol: "g ∘ f"
term: composition
domain: category_theory
class: canonical
definition: "Composition of composable morphisms"
aliases: []
relations:
  - kind: analogue
    key: functional_programming.compose
  - kind: dual_context
    key: category_theory.opposite
provenance:
  - issue: 320
  - proposal: notation-sets-evolution
status: active
confidence: reviewed
first_seen: 2026-08-22
last_verified: 2026-08-22
```

This is deliberately a specification shape, not a claim that the repository currently implements this exact schema.

## 4. Continuous evolution research loop

The vocabulary should evolve as repository knowledge evolves:

```text
DISCOVER
  ↓
NORMALIZE
  ↓
CLASSIFY
  ↓
CROSS-CHECK
  ↓
RELATE
  ↓
INDEX
  ↓
VALIDATE
  ↓
OBSERVE
  ↓
REVISE
  ↓
PUBLISH
  ↺
```

### Discover

Mine new issues, proposals, source notes, implementation paths, commits, agent reports, and domain references for new terminology or notation.

### Normalize

Map spelling, glyph, capitalization, and namespace variants to stable candidate keys without erasing the original surface form.

### Classify

Mark each candidate as canonical, alias, cross-domain analogue, domain-specific, or deprecated/legacy.

### Cross-check

Require a source/provenance record and distinguish repository convention from external mathematical or programming convention.

### Relate

Add typed relationships such as `alias_of`, `analogue_of`, `dual_of`, `composes_with`, `implements`, `specified_by`, `indexed_by`, and `supersedes`.

### Index

Connect entries to the existing ArchW1z and ICM index families and to the source issues/proposals/branches.

### Validate

Detect collisions, broken references, duplicate keys, missing provenance, and invalid classifications.

### Observe / revise / publish

Use implementation feedback, review outcomes, and newly discovered evidence to update the vocabulary while retaining an evolution ledger.

## 5. Relationship to #175

Issue #175 is the current operator-priority and master functional-gate reference. Its rules require small green rebased PRs, no force-push to master, and repo-gate + termux-smoke for merges. It also places documentation/comms work in P3 while preserving the operator rules as hard constraints.

Accordingly, this proposal is intentionally **documentation/specification-first**. It does not bypass #175 by treating the vocabulary as an implementation permission. Any executable index generator, compression integration, or workflow change should be a later proposal item/PR that cites its item ID and passes the applicable gates.

## 6. Relationship to existing repository indexes

The proposal is additive:

```text
                         ┌────────────────────┐
                         │ Living notation     │
                         │ lexicon/dictionary  │
                         └─────────┬──────────┘
                                   │
             ┌─────────────────────┼─────────────────────┐
             ▼                     ▼                     ▼
     ArchW1z concept/pointer   LLM map aliases      ICM relationships
             │                     │                     │
             └─────────────────────┼─────────────────────┘
                                   ▼
                         Grimoire compression
```

The objective is a stable semantic layer that can point into those systems rather than another monolithic index that becomes stale.

## 7. Research and expansion policy

1. Preserve source terminology before normalization.
2. Never infer equivalence solely from visual similarity.
3. Record domain and scope for every canonical entry.
4. Prefer typed relationships over prose-only cross-references.
5. Preserve historical aliases for search/migration.
6. Record evidence for semantic corrections and reclassification.
7. Regenerate derived indexes from authoritative records where practical.
8. Make drift detectable by CI rather than relying on manual memory.
9. Keep operator/security constraints from being weakened by compression or automation.
10. Treat external research as evidence to evaluate, not as an automatic repository truth.

## 8. Proposed next research pass (illustrative, not yet tracked)

The following are candidate future research directions that are not yet itemized as NSE-* entries in ITEMS.md and would need their own item before being treated as proposal work:

- Audit #320's linked issues (#309, #182, #126, #304, #196, #177, #208, #274) and map terminology overlap.
- Inventory existing index schemas and identify authoritative-vs-derived boundaries.
- Compare `ALIAS_INDEX`, `CONCEPT_INDEX`, `POINTER_INDEX`, `TOOL_INDEX`, and the context-relationship index for collision/overlap.
- Prototype a notation registry fixture and validator without changing runtime behavior.
- Define the minimum relation vocabulary required by #309 compression.
- Add a generated cross-reference view only after the source-of-truth model is accepted.

## 9. Provenance

- GitHub Issue #320 — Notation Sets (created 2026-08-22).
- GitHub Issue #309 — referenced by #320 as the Grimoire compression work.
- GitHub Issue #182 — referenced by #320 as related Grimoire work.
- GitHub Issue #175 — OPERATOR priority matrix and master functional gate; current governance constraint.
- Repository proposal process: `docs/proposals/PROCESS.md`.
- Repository proposal registry: `docs/proposals/registry.yaml`.
- Existing index artifacts listed above are repository evidence for integration points; this proposal does not claim they share one schema today.
