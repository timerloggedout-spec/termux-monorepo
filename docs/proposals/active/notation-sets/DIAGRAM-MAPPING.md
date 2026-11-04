# Diagram Mapping — notation → renderings (.mmd)

**Commission (owner, 2026-11-03):** the Group && Category Theory etc
notations ought to be able to map → `.mmd` [etc], + ELI5. This spec is
that mapping layer.

## Authority rule

The **notation of record is the SOURCE** (nomenclature-matrix seed,
treatment docs, NSE-023 packets). A diagram is a **rendering layer**:
citable, never the authority. Where a diagram and the notation differ,
the notation governs and the diagram is the defect.

## Export contract (every export, no exceptions)

1. **Fidelity header** — each `.mmd` opens with a comment block:
   source of record · export date · fidelity per construct rendered
   (lossless ∨ lossy) · **losses named** (what the drawing drops).
2. **ELI5 beside it** — every export ships a sibling `<name>.ELI5.md`:
   plain words, what the diagram shows + what it means, ∅ jargon —
   readable by a newcomer with none of the notation.
3. Exports live in `docs/proposals/active/notation-sets/diagrams/`.

## Construct mapping (fidelity stated per construct)

| Notation construct | .mmd rendering | Fidelity |
|---|---|---|
| concept (seed) | node (id + preferred label) | lossless |
| mapping / crosswalk (relation) | labeled edge (relation as label) | lossy: confidence + evidence_note + status dropped unless carried in the label |
| morphism / homomorphism | solid labeled arrow | lossy: domain/codomain laws not rendered |
| composition ∘ | chained arrows A → B → C | lossless (shape); associativity = annotation, not geometry |
| kernel (ker) | edge annotation naming ker | lossy: the set content of ker is not rendered |
| state structure (finite Stage + transitions) | `stateDiagram-v2` | lossless iff the enumeration is complete; lossy: guard/predicate content |
| dual-valence pair E^{T∧O} | one node, two reading subnodes | lossless (pairing preserved) |
| conversion κ_{T→O} (object part id_E) | dashed arrow labeled κ | lossy: id_E part + frame index must ride in label/note; ker κ named in note |
| proof content (≅ discharge, axioms) | — | **not exportable**: no honest diagram form; pointing at the packet/verdict is the rendering |

## Sibling formats (named only where honest)

- `.mmd` (Mermaid) — primary: graphs + state diagrams.
- `.dot` (Graphviz) — honest sibling for crosswalk graphs needing
  richer edge attributes (confidence as weight/label).
- Anything else is not claimed. A format that cannot carry the
  fidelity header + losses does not ship.

## Worked exports (this landing)

- `diagrams/crosswalk-group-category.mmd` (+ ELI5) — group_theory ⇔
  category_theory mappings of record from the seed.
- `diagrams/dual-valence-conversion.mmd` (+ ELI5) — the dual-valence
  treatment rendered (pair, κ, assimilation pipeline, ker note).
- E001 cycle state diagram (DoE EpochMethods Stage structure) —
  coordinated with DoE; lands when the Stage enumeration of record
  is received (transitions must be verbatim, ¬ reconstructed).
