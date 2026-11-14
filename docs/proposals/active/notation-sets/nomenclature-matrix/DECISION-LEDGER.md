# Nomenclature Matrix — Decision Ledger

**Status:** historical record and governance aid; not runtime authority  
**Scope:** nomenclature/notation research lineage only  
**Last verified against GitHub:** 2026-10-29

This ledger records repository decisions and implementation milestones tied to the referenced issues and pull requests. It separates confirmed repository events from design constraints and open work. It does not infer domain-science approval from a merge.

## Confirmed lineage

| Date (UTC) | Record | Confirmed event | Resulting boundary |
|---|---|---|---|
| 2026-08-22 | [Issue #320 — Notation Sets](https://github.com/timerloggedout-spec/termux-monorepo/issues/320) | Established the notation research surface. Its body includes category-theory notation, morphisms/arrows, composition, hom-sets, identities, functors, natural transformations, and cross-domain notation comparisons. | Issue content is repository research input; analogies and comparisons are not automatically formal equivalences. |
| 2026-10-04 | [Issue #1115 — Domain Composition Matrix](https://github.com/timerloggedout-spec/termux-monorepo/issues/1115) | Explicitly proposed a dedicated, versioned Domain Composition Matrix database, separate from the notation registry and generated INDEX views. | Domain-specific composition rules, typed constraints, evidence, confidence, lifecycle, and projections belong to that separate research database. |
| 2026-10-21 | [PR #1412](https://github.com/timerloggedout-spec/termux-monorepo/pull/1412) | Merged the initial sourced nomenclature equivalency matrix (rebased from #1309). Its PR description records a YAML-structure-verified workflow and a candidate seed of 4 concepts, 6 labels, 2 mappings, and 5 sources. | Establishes the initial repository artifact, not blanket approval of every seed assertion. |
| 2026-10-21 | [PR #1435](https://github.com/timerloggedout-spec/termux-monorepo/pull/1435) | Merged research expansion to 10 sources, 8 concepts, and 14 labels; added hidden_search_alias, research ledger, and manifest registration. | Added records remained candidate; W3C SKOS remained normative for SKOS semantics; Wikipedia remained orientation-only. |
| 2026-10-27 onward | [PR #1734](https://github.com/timerloggedout-spec/termux-monorepo/pull/1734) | Added assertion-level evidence provenance, SQLite evidence table, deterministic Markdown/JSON crosswalks, and stricter validation. | Evidence records are candidate provenance, not independent mathematical verification or runtime authority. The PR remains open until review and merge decisions are made. |

## Decisions and invariants carried forward

1. **Concepts are canonical; labels are contextual.** A string is a label attached to a concept, not the concept identity itself.
2. **Label equivalence and concept mapping are different assertions.** A preferred/alternative label relationship must not be conflated with a cross-concept mapping.
3. **Mapping relations remain typed.** Exact, close, broader, narrower, related, explanatory, analogical, translation, ambiguous, and contradictory relationships must not be flattened into a generic synonym.
4. **Candidate is the default research state.** Discovery, citation, generated output, or a passing structural validator does not itself establish domain acceptance.
5. **Evidence is claim-scoped.** A source's existence does not prove every assertion that cites it. Each evidence record must state its bounded claim and locator.
6. **Domain Composition Matrix remains separate.** #1115's database is not a synonym for the nomenclature matrix and must not be merged into it.
7. **Generated projections are derived artifacts.** CROSSWALK.md and CROSSWALK.json must be regenerated from seed.json, not edited independently.
8. **Human/domain review is explicit.** Never populate a reviewer, mark evidence accepted, or claim specialist approval unless that review actually occurred and is recorded.

## Open decisions / gates

- Obtain domain review for each claim whose status is to advance beyond candidate.
- Verify each source locator and excerpt against the cited source, including repository issue passages.
- Decide whether the nomenclature schema needs stronger database-level referential constraints for polymorphic assertion references (assertion_type + assertion_id).
- Define a versioning and deprecation policy for concepts, labels, mappings, and evidence records before downstream consumers rely on stable identifiers.
- Keep any Domain Composition Matrix implementation and its review lifecycle tracked under #1115 and its own artifacts.

## How to update this ledger

Add a row only when an issue, pull request, commit, or documented review provides a verifiable event. Include a direct link and describe what the record proves—not what it merely suggests. Do not rewrite historical rows to imply approval that was not recorded.
