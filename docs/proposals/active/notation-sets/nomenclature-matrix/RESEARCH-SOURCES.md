# Nomenclature Equivalency Matrix — Research Sources and Evidence Ledger

**Research snapshot:** 2026-10-20  
**Status:** evidence ledger; no candidate row is promoted by this document  
**Parent:** [Notation Sets #320](https://github.com/timerloggedout-spec/termux-monorepo/issues/320) · [Domain Composition Matrix #1115](https://github.com/timerloggedout-spec/termux-monorepo/issues/1115)

## Research question

How should one represent formal terminology, lay explanations, colloquial/community language, ad hoc names, abbreviations, hidden search aliases, and related concepts without falsely treating lexical resemblance as semantic equivalence?

## Findings supported by sources

### 1. Keep labels separate from concepts and mappings

The W3C [SKOS Reference](https://www.w3.org/TR/skos-reference/) models concepts with lexical labels and distinguishes preferred, alternative, and hidden labels. It also provides distinct semantic and cross-vocabulary mapping relationships, including hierarchical, associative, close-equivalent, and exact-equivalent links. The [SKOS Primer](https://www.w3.org/TR/skos-primer/) gives practical examples and explains the role of hidden labels in retrieval.

**Design consequence:** a label type answers “what kind of name is this?” A mapping relation answers “how are these two concepts related?” Never overload either field to mean both.

### 2. Sense and context must be explicit

Wolfram's [WordData documentation](https://reference.wolfram.com/language/ref/WordData.html) supports sense-specific lexical records and exposes definitions, synonyms, broader terms, narrower terms, usage fields, and usage types. Wolfram's [Concept entity documentation](https://reference.wolfram.com/language/ref/entity/Concept.html) includes alternate names, broader/narrower concepts, equivalent entities, similar entities, and WordNet sense information.

**Design consequence:** capture domain, language, sense, audience, and register where available. A general-language synonym result is a discovery lead, not proof that two technical concepts are interchangeable.

### 3. Colloquial language needs an explicit bridge to formal vocabularies

Markham and McLaughlin, [“CWLD: Mapping colloquial wet lab language to ontologies”](https://europepmc.org/article/PPR/PPR570729) (BioHackrXiv preprint, 2022; DOI [10.37044/osf.io/p85m9](https://doi.org/10.37044/osf.io/p85m9)), describe a mismatch between formal ontology terms and practitioners' colloquial language, and a project to collect colloquial expressions and map them to ontology terms.

**Design consequence:** include `colloquial` and `ad_hoc` as explicit label classes, preserve where the expression was observed, and record mapping evidence independently. The source supports the need for this class of workflow; it does not validate any unrelated project-specific slang.

### 4. Cross-vocabulary equivalence must not be assumed

DARIAH-Campus, [“Controlled Vocabularies and SKOS”](https://campus.dariah.eu/resources/hosted/controlled-vocabularies-and-skos), summarizes SKOS mapping distinctions such as exact, close, broader, narrower, and related match. The J. Paul Getty Trust's [CONA / Getty Vocabularies introduction](https://www.getty.edu/research/tools/vocabularies/cona_intro.pdf) describes equivalence, hierarchical, and associative thesaurus relationships and shows multilingual vocabulary practice.

The scholarly study [“Lexical-semantic Mapping between Chinese and English Controlled Vocabularies in the Domain of Chinese Art”](https://doaj.org/article/153f2f1b9bbf4044b5c8210307ec1ef4) reports that only about one-third of the examined NPM-CV terms mapped as exact equivalences to AAT terms, while many more had hierarchical relationships. This is a domain-specific study, not a universal rate; its value here is demonstrating that vocabulary mapping frequently produces non-exact relationships.

**Design consequence:** exact match should be the strongest and most carefully reviewed relation. Preserve close, broader, narrower, and related relations rather than collapsing them into “synonym.”

### 5. Near-synonymy is a separate lexical-semantic issue

The SciSpace search surfaced [“On the Differentiation Between Synonyms and Near-synonyms”](https://doi.org/10.3969/j.issn.1000-5218.2002.05.013). Its returned abstract distinguishes sameness of lexical meaning from similarity of meaning and discusses the role of conceptual correspondence.

**Evidence limitation:** the record was discovered through SciSpace's paper index; full-text verification and bibliographic cross-checking remain desirable before treating it as a primary theoretical authority.

### 6. Wikipedia is orientation, not normative authority

The [Wikipedia overview of SKOS](https://en.wikipedia.org/wiki/Simple_Knowledge_Organization_System) was found as an accessible entry point. Use it to navigate concepts, but cite the W3C Recommendation for normative claims about SKOS.

## Research resources and coverage

| Resource | Use in this pass | Evidence boundary |
|---|---|---|
| Wolfram | Looked up lexical sense, synonym, broader/narrower and concept properties | General lexical resources do not prove domain equivalence |
| Wikipedia | Located the SKOS overview | Orientation only; prefer W3C for normative claims |
| SciSpace | Discovered research on synonymy and near-synonymy | Search metadata/abstract; full-text verification pending |
| Parallel Search | Retrieved W3C SKOS, CWLD, Getty and mapping references | Search excerpts are discovery evidence; cited source pages remain the authority |
| Agentic Search by Liner | Cross-checked SKOS and controlled-vocabulary references | Search output is a research aid, not a normative source |
| Firecrawl | Retrieved relevant source snippets for W3C SKOS and CWLD and surfaced DARIAH resources | Scrape/search results do not replace source-level review |
| Scite | Not used | The offered trial required a payment card; no trial or paid subscription was activated |

## Vocabulary rules to encode

- `preferred_formal`: preferred technical name in a scoped domain.
- `preferred_plain_language`: reviewed explanation for a stated audience; not automatically a synonym.
- `alternative_synonym`: alternate lexical form for the same intended sense; evidence required.
- `colloquial`: informal community/practitioner expression with provenance.
- `ad_hoc`: locally coined or task-specific label; preserve local scope and author/source.
- `jargon`: community- or profession-specific usage; distinguish from the formal term.
- `abbreviation`: shortened form; expand and disambiguate where possible.
- `symbolic_notation`: symbol or expression whose semantics are domain-dependent.
- `historical` / `deprecated`: time-sensitive form; retain lifecycle and replacement links.
- `translation`: language-to-language relation, not automatic conceptual equivalence.
- `analogy`: explanatory comparison, never exact identity.
- `near_synonym` / `related_term`: discovery relations that do not assert interchangeability.
- `hidden_search_alias`: retrieval-only form that is not normally shown as a preferred label; spelling variants should not be promoted merely because they match a query.

## Promotion protocol

1. Preserve the exact observed expression and source locator.
2. Identify concept, domain, sense, language, audience, register, and time/context if known.
3. Classify the label independently from the concept mapping.
4. Record a relation type and source evidence for any cross-concept assertion.
5. Keep the item `candidate` until a reviewer confirms the scope and evidence.
6. Reject or downgrade exact equivalence when evidence only supports analogy, relatedness, or broader/narrower correspondence.
7. Keep search-engine results and repository discussion as provenance leads unless they directly substantiate the claim.

## Bibliography

- W3C. [SKOS Simple Knowledge Organization System Reference](https://www.w3.org/TR/skos-reference/).
- W3C. [SKOS Primer](https://www.w3.org/TR/skos-primer/).
- Wolfram Research. [WordData](https://reference.wolfram.com/language/ref/WordData.html).
- Wolfram Research. [Concept entity](https://reference.wolfram.com/language/ref/entity/Concept.html).
- Markham, D. W., & McLaughlin, J. A. (2022). [CWLD: Mapping colloquial wet lab language to ontologies](https://europepmc.org/article/PPR/PPR570729).
- DARIAH-Campus. [Controlled Vocabularies and SKOS](https://campus.dariah.eu/resources/hosted/controlled-vocabularies-and-skos).
- J. Paul Getty Trust. [Cultural Objects Name Authority: Introduction to the Getty Vocabularies](https://www.getty.edu/research/tools/vocabularies/cona_intro.pdf).
- Chen, S. [Lexical-semantic Mapping between Chinese and English Controlled Vocabularies in the Domain of Chinese Art](https://doaj.org/article/153f2f1b9bbf4044b5c8210307ec1ef4).
- [On the Differentiation Between Synonyms and Near-synonyms](https://doi.org/10.3969/j.issn.1000-5218.2002.05.013).
- Wikipedia contributors. [Simple Knowledge Organization System](https://en.wikipedia.org/wiki/Simple_Knowledge_Organization_System) (orientation only).
