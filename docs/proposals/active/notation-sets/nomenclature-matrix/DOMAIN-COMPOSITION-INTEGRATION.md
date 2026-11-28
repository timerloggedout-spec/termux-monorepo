# Nomenclature ↔ Domain Composition integration contract

## Purpose and ownership

This contract defines typed references from nomenclature concepts to records in the Domain Composition Matrix (DCM). The nomenclature seed remains the source of vocabulary concepts, labels, and semantic mapping candidates. The DCM seed remains the source of domain-specific entities, operations, notation conventions, and composition rules.

The integration file is `DOMAIN-COMPOSITION-LINKS.json`. It is a manually curated relationship registry, not a generated synonym table and not a merged database.

## Non-negotiable authority boundary

- Every link currently has `candidate` status.
- A link is a navigational/contextual reference, not a claim of semantic equivalence.
- A concept-to-domain reference records scope only.
- A concept-to-entity/operation reference indicates the DCM record that elaborates the concept.
- A concept-to-rule reference provides context; it does not certify the rule or the concept.
- Labels and nomenclature semantic mappings are not copied into DCM by this integration.
- No downstream runtime, index, or composition engine may treat these links as accepted authority.

In particular, Haskell monadic bind remains distinct from ordinary morphism/function composition. Similar high-level descriptions do not collapse their operation or law contracts.

## Record shape

Each link has a stable `link_id`, a nomenclature `concept_id`, a typed `target_type` and `target_id`, a constrained `relation`, lifecycle `status`, a bounded `basis`, and a mandatory `non_equivalence_note`.

| target_type | relation | Meaning |
|---|---|---|
| `domain` | `domain_scope` | Concept is scoped to this DCM domain |
| `entity_type` | `describes_entity_type` | DCM entity type elaborates the concept |
| `operation` | `describes_operation` | DCM operation elaborates the concept |
| `composition_rule` | `contextualized_by_rule` | DCM candidate rule provides domain-specific context |

The target type and relation must agree. Unknown target types, unknown identifiers, cross-domain links, duplicate IDs/edges, or missing semantic boundaries fail validation.

## Version and provenance contract

The links file declares its own `schema_version` and the schema versions of both source seeds. The validator compares these declarations with the actual source seeds. Consumers should retain the source repository commit alongside any cached links and revalidate whenever either seed changes.

A future schema change that renames/removes fields, changes field types, or changes relationship meaning requires a version increment. Additive compatible fields may remain within the current version.

## Lifecycle

Allowed states are `candidate`, `reviewed`, `accepted`, `rejected`, `deprecated`, and `superseded`. Promotion to `accepted` requires a real reviewer and review date. No reviewer or approval may be inferred from the author, CI, source seed, or presence of a link.

## Deliberate omissions

- The functional-programming left-to-right composition concept is not linked to Lean's `≫` merely because the notation is associated with composition. Its domain and direction conventions require a separate sourced decision.
- No blanket mapping is created between category-theory composition and Haskell bind.
- No labels, aliases, or semantic equivalency mappings are copied into the DCM.
- No API, automatic synchronization, transitive closure, or runtime lookup behavior is promised.

## Validation

Run:

```sh
python scripts/ci/validate_nomenclature_domain_links.py
python -m unittest tests/test_nomenclature_domain_links.py
```

The nomenclature workflow runs both checks alongside the existing nomenclature validator and regression suite.
