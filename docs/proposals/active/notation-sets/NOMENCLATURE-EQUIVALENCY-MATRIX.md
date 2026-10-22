# Nomenclature Equivalency Matrix — Research and Data Contract

**Status:** research proposal; labels and mappings are not runtime authority  
**Version:** 1.0  
**Parent work:** [Issue #320 — Notation Sets](https://github.com/timerloggedout-spec/termux-monorepo/issues/320), [Issue #1115 — Domain Composition Matrix](https://github.com/timerloggedout-spec/termux-monorepo/issues/1115)

## Purpose

Expand the notation matrices from lists of symbols into a governed crosswalk between a *concept* and the different names people and systems use for it: formal terminology, preferred labels, plain-language explanations, colloquial names, community jargon, abbreviations, historical names, ad hoc descriptions, misspellings, and names used by other domains.

The missing umbrella label is best expressed as **terminology / nomenclature equivalency mapping**. For a searchable structured resource, use **Nomenclature Equivalency Matrix** as the project name and **lexical label / semantic mapping** as the standards-aligned terms. “Equivalence” must be qualified: two strings can be alternative labels for one concept, or two concepts can be mapped as exact/close/broader/narrower/related. Those are different relationships.

## Design principles

1. **Concept first, labels second.** Assign a stable concept ID; do not make a string itself the canonical concept.
2. **Preferred does not mean universally best.** Preferred labels are scoped by language, audience, domain, and use case.
3. **Synonym is not a catch-all.** An abbreviation, colloquial phrase, analogy, related concept, translation, and deprecated term should not be silently promoted to exact synonym.
4. **Do not flatten semantic relationships.** A term may be related, broader, narrower, or only approximately equivalent.
5. **Evidence and provenance travel with each assertion.** Capture source URL/DOI, exact quote or locator where available, source type, retrieval date, reviewer, confidence, and status.
6. **Candidate first.** No researched label or cross-domain match becomes implementation/runtime authority merely because it is present in the matrix.
7. **Audience language is an access layer.** Plain-language labels explain concepts; they do not replace formal definitions or proof obligations.

## Proposed label-type vocabulary

| Label type | Meaning | Example pattern | Default equivalence interpretation |
|---|---|---|---|
| `preferred_formal` | Curated canonical term for a domain/context | “morphism” in category theory | Canonical label for one concept, not proof of cross-domain equivalence |
| `preferred_plain_language` | Reviewed explanation for non-specialists | “a structure-preserving arrow/map” | Explanatory paraphrase; not necessarily a synonym |
| `alternative_synonym` | Accepted alternate wording for the same sense | “identity map” / “identity function” where definitions align | Candidate synonym; record domain/sense |
| `colloquial` | Informal community or conversational wording | “glue these functions together” | Informal paraphrase, not automatically exact |
| `ad_hoc` | Locally coined, temporary, or author-specific label | “the pipe step” in a project note | Unverified until reviewed; preserve source context |
| `jargon` | Community-specific shorthand | team or subfield vocabulary | Scoped to community/domain |
| `abbreviation` | Initialism or shortened form | “CT” for category theory | Label variant, disambiguation required |
| `symbolic_notation` | Symbol or expression used to denote the concept/operation | `g ∘ f`, `f ; g`, `g . f` | Must record syntax, direction/order, and domain convention |
| `historical` | Earlier or obsolete term | source-era terminology | Preserve date and source; may be deprecated |
| `deprecated` | Term discouraged by an identified authority | deprecated API/term name | Search compatibility may be retained; do not recommend as preferred |
| `misspelling` | Common or observed spelling error | typo variant | Search-only/hidden label, never semantic equivalence evidence |
| `translation` | Label in another natural language | English/French label pair | Language mapping, not necessarily cross-cultural concept identity |
| `analogy` | Teaching comparison to a different familiar concept | “like a pipeline” | Related explanatory analogy, explicitly not identity |
| `near_synonym` | Overlapping but non-identical meaning | context-sensitive near-equivalent | `close_match` only when evidence supports it |
| `related_term` | Associated concept without equivalence | “functor” related to “morphism” | Related, not interchangeable |
| `external_identifier` | URI, ontology ID, API key, or code | concept URI | Identity is resolved by identifier/provenance, not label string alone |

These are project-level controlled values, not a claim that an external standard defines this exact enumeration. Map them to SKOS properties where appropriate (see sources).

## Semantic relationship vocabulary

| Relation | Use when | Do not use when |
|---|---|---|
| `same_concept_label` | Different labels denote the same concept in the same intended sense | The wording merely explains or resembles the concept |
| `exact_match` | Two concepts are sufficiently equivalent for broad interchange in retrieval/use | Definitions, scope, or operational behavior differ |
| `close_match` | Concepts are near-equivalent but interchangeability is limited/contextual | The concepts are simply associated |
| `broad_match` | Target concept is broader than source | They are exact synonyms |
| `narrow_match` | Target concept is narrower than source | They are exact synonyms |
| `related_match` | Concepts are associated but neither equivalence nor hierarchy is established | The user expects substitution |
| `explains` | Plain-language statement explains a formal concept | Explanation is itself a formal definition |
| `analogy_to` | Term is a pedagogical analogy | The compared concepts are identical |
| `translates_to` | Language-specific rendering | Translation is assumed to preserve every technical nuance |
| `supersedes` | A governed term/version replaces an earlier one | The older term must be erased from history |
| `ambiguous_with` | Same string has multiple senses or concepts | Disambiguation has been established |
| `contradicts` | Sources make incompatible claims about term meaning | Difference is only stylistic |

W3C SKOS distinguishes preferred, alternative, and hidden labels and distinguishes exact, close, broader, narrower, and related mappings. That is the core external design precedent. Use SKOS `prefLabel`, `altLabel`, and `hiddenLabel` for lexical labels where useful; use `exactMatch`, `closeMatch`, `broadMatch`, `narrowMatch`, and `relatedMatch` for concept mappings rather than treating all links as synonyms.

## Required record shape

Minimum conceptual JSON shape (illustrative, not yet a migration or executable schema):

```json
{
  "concept_id": "stable-namespace:concept-name",
  "concept_version": 1,
  "domain_id": "category_theory",
  "preferred_label": {
    "text": "morphism",
    "language": "en",
    "audience": "expert",
    "register": "formal",
    "source_id": "source-or-authority-id"
  },
  "labels": [
    {
      "text": "arrow",
      "label_type": "alternative_synonym",
      "language": "en",
      "audience": "learner",
      "register": "technical",
      "sense_scope": "category_theory",
      "relation_to_concept": "same_concept_label",
      "status": "candidate",
      "confidence": 0.65,
      "evidence_ids": ["evidence-001"]
    },
    {
      "text": "a structure-preserving arrow",
      "label_type": "preferred_plain_language",
      "language": "en",
      "audience": "general",
      "register": "plain_language",
      "relation_to_concept": "explains",
      "status": "candidate",
      "confidence": 0.7,
      "evidence_ids": ["evidence-002"]
    }
  ],
  "definition": "Definition sourced from an authoritative domain reference.",
  "status": "candidate",
  "version": 1,
  "review": {
    "reviewer": null,
    "reviewed_at": null,
    "decision_note": "Do not promote without source verification."
  }
}
```

### Evidence record

Every non-trivial equivalency claim should have a separate evidence record:

- `evidence_id`, `concept_id` and/or `mapping_id`
- source title, publisher/organization, URL, DOI or stable identifier
- source class: standard, primary technical documentation, scholarly publication, encyclopedia, community usage, repository discussion, or model-generated lead
- exact excerpt and locator (section, page, line, issue comment, commit)
- access/retrieval date and publication/update date if known
- evidence role: definition, supports, contrasts, example-of-usage, historical-attestation
- reviewer, confidence, status, and limitations

A search result or model-generated suggestion is a **discovery lead**, not sufficient evidence by itself. Prefer standards and primary sources for formal semantics, scholarly literature for research claims, domain documentation for implementation conventions, and repository comments/commits for project-local usage.

## Illustrative notation records from Issue #320

| Concept/operation | Formal/domain label | Plain-language rendering | Important guardrail |
|---|---|---|---|
| Category-theoretic composition | (g \circ f) | “apply (f), then (g)” | Mathematical convention composes right-to-left in the expression |
| Left-to-right composition convention | `f ; g` or `f >>> g` in some ecosystems | “do (f), then (g)” | Same conceptual operation only after confirming type/order conventions |
| Lean composition | `f ≫ g` | “compose (f) followed by (g)” | Preserve Lean's type and argument conventions; do not equate syntax blindly |
| Haskell monadic bind | `m >>= f` | “feed a computation's result into the next step” | **Not simply ordinary function composition**; monadic structure and types matter |
| Identity morphism/function | `id_A`, `1_A`, `id` | “leave the value/structure unchanged” | Scope and type matter; notation can collide across domains |
| Exponential object | (Y^X) | “an object of maps from (X) to (Y)” in a suitable closed category | Do not collapse categorical exponential objects with set cardinality ( |Y|^{|X|} ) |

These are seed examples, not promoted equivalences. Verify each against authoritative domain references and the exact repository discussions before changing any implementation or notation registry.

## Workflow and promotion policy

1. **Discover:** extract candidate terms from Issue #320, related issues/PRs, comments, branch docs, and commits.
2. **Normalize:** assign concept IDs; preserve raw source text and commit/comment URLs.
3. **Classify:** label type, audience, language, domain, register, temporal status, and proposed relation.
4. **Evidence:** attach sources supporting the meaning and the asserted relationship.
5. **Disambiguate:** flag homonyms, overloaded symbols, domain conflicts, direction/order mismatches, and near-synonyms.
6. **Review:** human/domain reviewer approves, rejects, or requests evidence.
7. **Validate:** enforce schema, controlled values, referential integrity, source links, confidence bounds, and no unsupported exact matches.
8. **Project:** generate notation/INDEX/ICM views from the authoritative data; do not hand-maintain competing copies.
9. **Version:** keep immutable history of changes, rationale, provenance, and reviewer decisions.
10. **Audit:** periodically detect stale URLs, source changes, contradictory definitions, deprecated labels, and unreviewed candidates.

Suggested lifecycle: `discovered → candidate → evidence-backed → reviewed → accepted`, with `rejected`, `deprecated`, and `superseded` as explicit outcomes. Do not use confidence alone as a substitute for review or formal semantic checks.

## Source references

1. **W3C, SKOS Simple Knowledge Organization System Reference** — defines preferred/alternative/hidden lexical labels and semantic/mapping relationships, including exact/close/broader/narrower/related mappings.  
   https://www.w3.org/TR/skos-reference/
2. **W3C, SKOS Primer** — examples of preferred labels, synonyms, near-synonyms, abbreviations, acronyms, misspellings, and mapping concepts.  
   https://www.w3.org/TR/skos-primer/
3. **Wolfram Language, WordData** — sense-sensitive synonym and broader/narrower-term lookup; illustrates why word matching must be scoped to meaning/sense.  
   https://reference.wolfram.com/language/ref/WordData.html
4. **Wolfram Function Repository, SynonymGraph** — synonym graph exploration; useful as a candidate-discovery aid, not an authority for technical equivalence.  
   https://resources.wolframcloud.com/FunctionRepository/resources/SynonymGraph/
5. **Wikipedia, Category (mathematics)** — general orientation for category-theory terminology; use as a tertiary overview and verify formal claims against textbooks or authoritative domain sources.  
   https://en.wikipedia.org/wiki/Category_(mathematics)
6. **Repository source: Issue #320 — Notation Sets** — origin of the cross-domain notation matrix and its candidate comparisons.  
   https://github.com/timerloggedout-spec/termux-monorepo/issues/320
7. **Repository source: Issue #1115 — Domain Composition Matrix** — source-of-truth boundary and evidence/versioning contract.  
   https://github.com/timerloggedout-spec/termux-monorepo/issues/1115
8. **Repository source: Issue #274 — Linguist/Grimoire/A2A governance** — related guidance on canonical sources, symbolic mappings, and separation of representation from security guarantees.  
   https://github.com/timerloggedout-spec/termux-monorepo/issues/274

## Research limitations and resource policy

- Wolfram's semantic/context search returned useful documentation for sense-aware synonyms and lexical graphs, but its direct natural-language queries for this project's custom phrase did not identify an established named standard. Therefore this proposal uses “Nomenclature Equivalency Matrix” as a project label, not as a claim that a universal standard already exists under that name.
- Web/search snippets are discovery evidence; cite the underlying standard/page in any promoted record.
- Scite connection in this session presented a credit-card-required seven-day trial. No trial was activated. Scite-derived claims are therefore not asserted in this document.
- Scholarly search can expand the bibliography in a later pass; this initial version is grounded in W3C standards, Wolfram documentation, and the repository's own provenance.

## Research expansion: colloquial, ad hoc, and near-equivalent terminology

The candidate seed now adds explicit concepts for lexical labels, controlled vocabularies, colloquial-to-formal mapping, and near-synonymy. The seed also records source leads from W3C, Wolfram, DARIAH-Campus, the J. Paul Getty Trust, Europe PMC/BioHackrXiv, Wikipedia, and scholarly linguistic research. Wikipedia is orientation-only; normative claims should be verified against the standard or primary research source.

### Terminology rule: label type is not mapping relation

A label is a string attached to a concept. A mapping is an assertion connecting concepts or vocabularies. Do not represent colloquial language as an exact synonym merely because a practitioner uses it to discuss the same general topic. Store it as a candidate label or a scoped mapping, and preserve its register, audience, language, domain, source, and evidence.

### Candidate vocabulary additions

- `hidden_search_alias`: a retrieval-only spelling or form that should not ordinarily be displayed as the preferred user-facing label. This is aligned with the SKOS hidden-label use case for search indexing; it is not an endorsement of the spelling.
- `preferred_plain_language`: a reviewed explanation for a specified audience, not necessarily a lexical synonym.
- `colloquial` / `ad_hoc`: a community-used or locally coined expression. Keep provenance and local scope; do not silently globalize it.
- `near_synonym` / `related_term`: useful for discovery but not sufficient evidence for interchangeability.

The implementation remains candidate-only. Source discovery by Wolfram, Parallel Search, Liner, Firecrawl, or SciSpace is a provenance lead; it does not independently promote a row. Scite was not used because its trial gate required a payment card, and no subscription was activated.
