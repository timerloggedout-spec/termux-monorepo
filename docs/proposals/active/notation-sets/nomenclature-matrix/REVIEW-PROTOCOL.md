# Nomenclature evidence review protocol

## Purpose

This protocol defines a reproducible human review process for candidate concepts, labels, mappings, and claim-level evidence. The validator checks structural integrity; it does not decide whether a mathematical or domain claim is true.

## Review unit

Review the smallest independently assessable assertion: a concept definition, a label-to-concept assignment, a mapping relation between concepts, or a claim-level evidence record. A source bibliography entry alone is not an assertion and must not be treated as support for every record that references it.

## Evidence record minimum

Each `evidence_records` entry identifies a stable evidence ID, one known source ID, an assertion type (`concept`, `label`, or `mapping`) and matching assertion ID, a bounded claim, a followable locator, a short faithful excerpt when available, canonical retrieval date (`YYYY-MM-DD`), reviewer only after an actual review, and lifecycle status.

Do not turn search snippets, search-provider output, or repository discussion into primary-domain evidence without recording that limitation.

## Lifecycle

The schema and validator accept: `discovered`, `candidate`, `evidence_backed`, `reviewed`, `accepted`, `rejected`, `deprecated`, and `superseded`.

| Status | Meaning | Required action |
|---|---|---|
| `discovered` | Untriaged lead | Capture origin; do not rely on it |
| `candidate` | Scoped hypothesis awaiting sufficient evidence/review | Keep out of authoritative consumers |
| `evidence_backed` | Supporting evidence attached and checked for traceability | Record boundaries; domain correctness is not implied |
| `reviewed` | A reviewer assessed the assertion | Record reviewer and disposition in review history |
| `accepted` | Explicit domain acceptance for the stated scope | Require a nonblank reviewer; preserve evidence and scope |
| `rejected` | Reviewed and not accepted | Record reason; do not silently recycle the claim |
| `deprecated` | Previously used record should no longer be preferred | Point to successor where applicable |
| `superseded` | Replaced by a newer record | Link replacement and preserve history |

The current validator specifically requires a nonblank reviewer for `accepted` evidence records. This protocol applies the same accountability principle to human acceptance decisions on concepts, labels, and mappings, even where the current validator does not enforce a reviewer field for those record types.

## Reviewer procedure

1. **Check identity and scope.** Confirm assertion ID, domain, notation convention, audience, language, and register.
2. **Open the source.** Follow the locator to the cited passage; do not rely only on the source title or abstract.
3. **Test claim fit.** Confirm the excerpt supports the bounded claim and does not overstate the source.
4. **Check counterexamples and convention variance.** For mathematical notation, inspect composition order, typing, category/context, and domain-specific conventions.
5. **Choose a relation deliberately.** Prefer `related_match`, `explains`, `analogy_to`, or `ambiguous_with` when equivalence is not established. Do not promote string similarity to `exact_match`.
6. **Record disposition.** Reviewer, date, rationale, and scope must be auditable. Rejection is a valid outcome.
7. **Regenerate projections.** Run `python scripts/ci/build_nomenclature_crosswalk.py`; never hand-edit generated crosswalk files.
8. **Run validation.** Run `python scripts/ci/validate_nomenclature_matrix.py` and `python -m unittest tests/test_nomenclature_matrix.py`.

## Independence and conflicts

- The record author should not be the sole domain approver for a high-impact equivalence claim.
- Prefer a reviewer with demonstrated competence in the relevant domain and notation convention.
- If independent review is unavailable, leave the record at its current state and document the gap.
- Do not invent reviewer names, credentials, source locators, or approval dates.

## Promotion boundary

No record becomes runtime authority solely because it is present in `seed.json`, `CROSSWALK.md`, `CROSSWALK.json`, a passing validator, or a green CI workflow. Runtime adoption requires a separately documented decision by the owning system and its governance process.
