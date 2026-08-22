# ITEMS — notation-sets-evolution

## NSE-001 — Canonical notation taxonomy

Define a machine-readable-friendly taxonomy distinguishing:

1. **Canonical** — notation normative for the originating mathematical/computational domain.
2. **Alias** — semantically equivalent shorthand accepted by the same domain or repository convention.
3. **Cross-domain analogue** — structurally parallel notation whose meaning must not be assumed identical.
4. **Domain-specific syntax** — notation whose semantics depend on a particular language, framework, or calculus.
5. **Deprecated/legacy** — retained for search and migration but not emitted by new tooling.

**Initial seed from #320:** morphism `f: A → B`; composition `g ∘ f`; identity `id_A`; functor `F: C → D`; natural transformation `α: F ⇒ G`; opposite category `C^op`; product/coproduct duality; exponential `Y^X`.

## NSE-002 — Grimoire compression contract

Specify how notation tokens participate in #309/#182 compression without collapsing distinct semantics. Compression MUST preserve the semantic category, directionality, composition order, identity behavior, and domain scope needed to reconstruct the expanded form.

## NSE-003 — Living index/glossary/dictionary

Create a continuously regenerated vocabulary layer that records, for every term or symbol:

- canonical key and display form;
- definition;
- domain/category;
- aliases and observed variants;
- semantic relations and duals;
- source issues, proposals, commits, and implementation paths;
- confidence/provenance;
- lifecycle state;
- first-seen and last-verified timestamps;
- replacement/deprecation links.

The registry should cross-link to existing `archwiz/CONCEPT_INDEX.md`, `archwiz/POINTER_INDEX.md`, `archwiz/TOOL_INDEX.md`, `archwiz/METHODOLOGY_INDEX.md`, `workspace/llm_map/ALIAS_INDEX.md`, `workspace/llm_map/INDEX_OVERVIEW.md`, and `docs/icm/objects/knowledge/context-relationship-index.md` rather than creating an isolated competing index.

## NSE-004 — Continuous research and expansion loop

Establish a repeatable research loop:

`discover → normalize → classify → cross-check → relate → index → validate → observe → revise → publish`

Inputs include new issues, proposal sources, implementation changes, agent observations, mathematical/computational references, and repository terminology. Every expansion records provenance and avoids silently promoting an analogy into a canonical definition.

## NSE-005 — Context-relationship integration

Use the proposal's notation keys as stable semantic anchors for context-relationship mapping. A notation entry can point to issues, proposals, branches, files, tools, and related concepts; it does not replace those source artifacts.

## NSE-006 — Operator/CI governance coupling

Align implementation with #175's live operator rules: no force-push to master; prefer small green rebased PRs; require `repo-gate` + `termux-smoke`; keep changes extractable; and treat the notation registry as documentation/specification until separately accepted for execution.

## NSE-007 — Validation and drift detection

Add validation for:

- duplicate canonical keys;
- alias collisions;
- malformed relations;
- missing provenance;
- broken issue/file/branch links;
- canonical-vs-domain-specific classification errors;
- stale entries whose source has materially changed;
- index entries that diverge from generated outputs.

## NSE-008 — Evolution ledger

Maintain an auditable evolution ledger for additions, reclassifications, aliases, deprecations, and semantic corrections. Changes should be attributable to a source artifact and review disposition rather than overwritten in place without history.

## Acceptance criteria

- #320, #309, #182, and #175 are explicitly connected in the proposal registry/source.
- Canonical notation is separated from aliases and domain-specific syntax.
- The glossary/index design has provenance and lifecycle semantics.
- Existing repository indexes are treated as integration targets, not discarded.
- Execution work remains gated by proposal acceptance and repository gates.
