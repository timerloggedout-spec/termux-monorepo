# Nomenclature Evidence — Review and Acceptance Protocol

**Status:** proposed governance protocol  
**Applies to:** concepts, labels, mappings, and claim-level evidence in this nomenclature research lane  
**Authority boundary:** this protocol does not grant runtime authority or replace domain-owner approval.

## 1. Lifecycle meaning

The seed/schema currently support these lifecycle values:

| Status | Operational meaning |
|---|---|
| discovered | Identified as a possible concept, label, mapping, or evidence lead; not yet screened. |
| candidate | Retained for investigation with an explicit provisional interpretation. |
| evidence_backed | Required claim-level evidence has been attached and checked for provenance completeness; this is not equivalent to specialist acceptance. |
| reviewed | A named reviewer has examined the bounded claim and recorded a disposition. |
| accepted | The appropriate domain authority has explicitly accepted the assertion for its stated scope and use. |
| rejected | Reviewed and not accepted; preserve the reason and provenance. |
| deprecated | Previously usable record is no longer recommended; retain history and replacement guidance where known. |
| superseded | Replaced by a newer record; preserve the successor reference and historical identity. |

A status transition is a governance decision, not a side effect of validation or code generation. Do not skip directly from discovery to acceptance.

## 2. Minimum evidence record

Each evidence record must identify:

- a stable evidence ID;
- a known source ID;
- an assertion type (concept, label, or mapping) and the corresponding assertion ID;
- a bounded claim stating what the passage supports and what it does not support;
- a reproducible locator (section, heading, page, paragraph, DOI section, or repository discussion location);
- a short, faithful excerpt where available;
- canonical retrieval date (YYYY-MM-DD);
- reviewer identity only after an actual review;
- lifecycle status.

A source bibliography entry alone is not claim-level evidence. A broad URL without a useful locator is insufficient for a high-confidence decision. If no stable excerpt exists, explain the limitation in the claim and provide the most precise available locator.

## 3. Review procedure

1. **Resolve the assertion.** Confirm that the referenced concept, label, or mapping exists and that the assertion ID is correct.
2. **Inspect the primary passage.** Open the cited source and verify that the locator resolves to the stated passage. Prefer normative standards or primary research for claims within their scope.
3. **Check the claim boundary.** Confirm that the excerpt supports the claim as written; record limitations, scope, assumptions, and counterexamples.
4. **Check semantic type.** Determine whether the assertion is a label, exact match, close match, broader/narrower relation, related term, explanation, analogy, translation, ambiguity, or contradiction. Do not promote similarity to equivalence.
5. **Check domain competence.** Route specialist mathematical, scientific, programming-language, or standards claims to an appropriate reviewer. A general repository maintainer may validate structure but cannot substitute for domain expertise.
6. **Record disposition.** Record reviewer, date, status, rationale, and any required follow-up in the repository's review record. Do not invent reviewer identities or imply approval from an automated agent.
7. **Regenerate projections.** Run python scripts/ci/build_nomenclature_crosswalk.py after seed changes and commit both generated projections with the source change.
8. **Validate.** Run python scripts/ci/validate_nomenclature_matrix.py and python -m unittest tests/test_nomenclature_matrix.py, plus the dedicated workflow.

## 4. Acceptance gate

An assertion may move to accepted only when all applicable conditions are met:

- the assertion has a bounded, unambiguous definition and stable identifier;
- claim-level evidence is traceable to a verified passage;
- the evidence supports the exact relationship type being asserted;
- scope, language, audience, domain, and relevant conventions are explicit;
- conflicts or contrary evidence are recorded and resolved or clearly bounded;
- an appropriate human/domain reviewer is named and has explicitly approved the assertion;
- the acceptance rationale and date are recorded;
- downstream impact and versioning/deprecation implications are understood.

For a mapping between two concepts, acceptance must address both concepts and the relationship—not merely the similarity of their labels. For mathematical notation, acceptance must preserve convention differences (including operation order) and must not infer equality of operations from visual resemblance.

## 5. Rejection, supersession, and rollback

- Rejection preserves the record and rationale; do not silently delete failed candidates.
- Supersession points to a successor record and explains the change.
- Deprecation states whether the record is unsafe, obsolete, ambiguous, or merely discouraged.
- If new evidence invalidates an accepted claim, open a review/change record promptly, mark the affected record for review, and prevent stale projections from being represented as current approval.
- Never rewrite historical evidence to match a later decision.

## 6. Automated versus human responsibilities

| Automated checks may establish | Automated checks cannot establish |
|---|---|
| IDs are unique and references resolve within the seed. | That a cited source is authoritative for a domain claim. |
| Required provenance fields and canonical date shape are present. | That an excerpt accurately represents its source or proves the claim. |
| SQLite constraints and deterministic projections work. | That two mathematical or scientific concepts are equivalent. |
| Generated files are fresh and tests pass. | That a domain expert reviewed or approved the assertion. |

## 7. Current PR #1734 disposition

The current seed evidence records are candidate research provenance. Reviewer fields are intentionally empty. The bind/composition candidate remains a low-confidence related_match, not an equivalence assertion. No evidence should be promoted to accepted merely to make the matrix appear complete.
