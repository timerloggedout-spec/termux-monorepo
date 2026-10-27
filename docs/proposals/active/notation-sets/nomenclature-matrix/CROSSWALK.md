# Nomenclature Equivalency Crosswalk

Generated from seed.json by scripts/ci/build_nomenclature_crosswalk.py. Do not edit by hand.
Candidate research data only: this projection does not promote labels or mappings to accepted/runtime authority.

## Concept and label crosswalk

| Concept ID | Domain | Preferred concept label | Definition | Label | Label type | Language | Audience | Register | Status | Sources |
|---|---|---|---|---|---|---|---|---|---|---|
| category_theory.composition | category_theory | morphism composition | Composition combines composable morphisms, with order conventions determined by notation. | glue the arrows together | ad_hoc | en | learner | colloquial | candidate | issue-320 |
| category_theory.composition | category_theory | morphism composition | Composition combines composable morphisms, with order conventions determined by notation. | apply one mapping, then the next | preferred_plain_language | en | general | plain_language | candidate | issue-320 |
| category_theory.morphism | category_theory | morphism | A morphism is an arrow in a category; exact formal properties depend on the category. | arrow | alternative_synonym | en | learner | technical | candidate | issue-320 |
| category_theory.morphism | category_theory | morphism | A morphism is an arrow in a category; exact formal properties depend on the category. | morphism | preferred_formal | en | expert | formal | candidate | issue-320 |
| category_theory.morphism | category_theory | morphism | A morphism is an arrow in a category; exact formal properties depend on the category. | a structure-respecting arrow | preferred_plain_language | en | general | plain_language | candidate | issue-320 |
| haskell.monadic_bind | haskell | monadic bind | The operation commonly written >>=, combining a monadic value with a function returning a monadic value. | >>= | symbolic_notation | und | expert | formal | candidate | issue-320 |
| knowledge_organization.controlled_vocabulary | knowledge_organization | controlled vocabulary | A curated set of terms used consistently to describe, index, retrieve, or organize information; mappings between vocabularies require explicit relationship types. | controlled vocabulary | preferred_formal | en | expert | formal | candidate | dariah-controlled-vocabularies |
| knowledge_organization.controlled_vocabulary | knowledge_organization | controlled vocabulary | A curated set of terms used consistently to describe, index, retrieve, or organize information; mappings between vocabularies require explicit relationship types. | a curated set of agreed terms | preferred_plain_language | en | general | plain_language | candidate | dariah-controlled-vocabularies, getty-cona-intro |
| knowledge_organization.lexical_label | knowledge_organization | lexical label | A language-tagged string used to name or refer to a concept; preferred, alternative, and hidden labels serve different presentation and retrieval roles. | lexical label | preferred_formal | en | expert | formal | candidate | w3c-skos-reference |
| knowledge_organization.lexical_label | knowledge_organization | lexical label | A language-tagged string used to name or refer to a concept; preferred, alternative, and hidden labels serve different presentation and retrieval roles. | the words used to name a concept | preferred_plain_language | en | general | plain_language | candidate | w3c-skos-primer |
| linguistics.near_synonymy | lexical_semantics | near-synonymy | A relationship between expressions with similar but not necessarily identical meaning; context and sense must be checked before treating them as interchangeable. | near-synonymy | preferred_formal | en | expert | formal | candidate | synonyms-near-synonyms-research |
| linguistics.near_synonymy | lexical_semantics | near-synonymy | A relationship between expressions with similar but not necessarily identical meaning; context and sense must be checked before treating them as interchangeable. | words that mean almost the same thing, but not always | preferred_plain_language | en | general | plain_language | candidate | synonyms-near-synonyms-research, wolfram-worddata |
| terminology.colloquial_to_formal_mapping | terminology_management | colloquial-to-formal terminology mapping | A documented association between practitioner or community language and a formal vocabulary concept, preserving the source expression and the confidence and scope of the mapping. | colloquial-to-formal terminology mapping | preferred_formal | en | expert | formal | candidate | cwld-colloquial-ontology |
| terminology.colloquial_to_formal_mapping | terminology_management | colloquial-to-formal terminology mapping | A documented association between practitioner or community language and a formal vocabulary concept, preserving the source expression and the confidence and scope of the mapping. | colloquial wet-lab language | related_term | en | practitioner | colloquial | candidate | cwld-colloquial-ontology |

## Semantic mapping candidates

| Mapping ID | Source concept | Relation | Target concept | Status | Confidence | Sources | Evidence note |
|---|---|---|---|---|---:|---|---|
| map-bind-not-compose |haskell.monadic_bind |related_match |category_theory.composition |candidate |0.35 |issue-320 |Keep related rather than exact: typeclass/monadic semantics and ordinary composition differ. |
| map-morphism-arrow |category_theory.morphism |same_concept_label |category_theory.morphism |candidate |0.5 |issue-320 |Label-level candidate inherited from Issue #320; domain review required. |

## Claim-level evidence

| Evidence ID | Assertion | Source | Locator | Claim boundary | Excerpt | Retrieved | Reviewer | Status |
|---|---|---|---|---|---|---|---|---|
| ev-bind-related-issue320 |mapping:map-bind-not-compose |issue-320 |Issue body > Core Category Theory Notation > Composition; and Type Theory & Functional Prog. row |Issue #320 places >>= in an alternative-composition discussion. This is a discovery lead only; the seed intentionally retains a low-confidence related_match rather than asserting equivalence. |Alternative Diagrammatic Composition: f ; g or f >>= g |2026-10-27 |unassigned |candidate |
| ev-morphism-arrow-issue320 |label:lbl-morphism-arrow |issue-320 |Issue body > Core Category Theory Notation > opening paragraph |Issue #320 explicitly describes morphisms as arrows; retain this as a source-backed alternate label candidate pending domain review. |objects (A, B, C) and morphisms (arrows) between them |2026-10-27 |unassigned |candidate |
| ev-morphism-formal-issue320 |label:lbl-morphism-formal |issue-320 |Issue body > Core Category Theory Notation > Morphism Assignment |Issue #320 names morphism notation as a core category-theory item; this supports discovery of the formal label, not external mathematical verification. |Morphism Assignment: f: A → B |2026-10-27 |unassigned |candidate |
| ev-morphism-mapping-issue320 |mapping:map-morphism-arrow |issue-320 |Issue body > Core Category Theory Notation > opening paragraph |The source uses “morphisms (arrows)” parenthetically; this supports a candidate same-concept label relationship, but does not itself constitute independent peer-reviewed evidence. |morphisms (arrows) between them |2026-10-27 |unassigned |candidate |

## Interpretation rules

- A label is a name or expression for a concept; it is not itself a mapping between concepts.
- same_concept_label, exact_match, close_match, broad_match, narrow_match, and related_match are distinct relations and must not be collapsed.
- Candidate status is preserved from the seed. A generated row is not approval, review, or mathematical verification.
- Evidence excerpts and locators are research aids; reviewers must inspect the cited source before accepting a claim.
