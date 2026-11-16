# GRIMOIRE Siglary-Compatible Notation Profile

**Profile ID:** `grimoire.siglary-bridge.v1`  
**Status:** Proposal only. This document does not redefine or reserve Siglary's canonical operator grammar.

## 1. Design intent

Provide compact, machine-readable operators for recipe descriptions and Do statements while preserving a full canonical SRM record. Micro-dense notation is a view/authoring shorthand, never the sole source of truth.

## 2. Namespace and collision rules

- Canonical owner: `grimoire.siglary-bridge.v1`.
- Existing Siglary registry remains authoritative for its operators.
- An operator is adopted only after registry lookup, collision review, semantics, examples, parser tests and versioning.
- Unknown operators are rejected or preserved as opaque extension data; they are never guessed.
- Every shorthand expands to canonical SRM fields.

## 3. Proposed operator vocabulary

| Token | Meaning | Canonical expansion |
|---|---|---|
| `R:` | Recipe identity | `recipe_id` |
| `V:` | Revision/schema version | `revision`, `schema_version` |
| `I:` | Ingredient set | `ingredients[]` |
| `P:` | Preparation/preconditions | `preparation[]` |
| `DO:` | Procedure operation(s) | `procedure[]` |
| `ENV:` | Execution environment | `environment` |
| `OUT:` | Expected outputs | `outputs[]` |
| `EVAL:` | Evaluation contract | `evaluation` |
| `PROV:` | Provenance | `provenance` |
| `LINK:` | Typed graph relation | graph edge |
| `ALT:` | Candidate alternative | `ALTERNATIVE_TO` candidate edge |
| `SUPER:` | Supersession | `SUPERSEDES` edge |
| `?=` | Unknown/unresolved | explicit unknown state |
| `!>` | Policy/admission boundary | policy gate reference |
| `=>` | Produces/transforms | `PRODUCES` / `TRANSFORMS` |
| `&` | Concurrent group | parallel group; only when dependencies permit |
| `;` | Sequential separator | explicit operation ordering |
| `@` | Immutable reference | source/revision/evidence reference |

## 4. Compact Do statement

Illustrative syntax:

```text
R:grimoire://recipe/example/normalize-data
V:grimoire.srm.v1
I:[source@sha256:..., schema@v2, policy@policy-id]
P:DO(validate-input); DO(normalize-fields)
DO(parse) ; DO(transform) ; DO(emit)
ENV:runtime@pinned, network=deny, resources=bounded
OUT:dataset@schema-v1, receipt@execution
EVAL:tests@sha256:..., status=?=
PROV:repo@commit, extractor@version
```

This is an illustrative shorthand, not a committed parser grammar. The schema is canonical and controls validity.

## 5. DO statement contract

A `DO` statement MUST specify:
- Operation identity and type.
- Declared inputs and outputs.
- Dependency ordering or concurrency group.
- Effect class and policy reference.
- Timeout/retry/idempotency behavior where applicable.
- Evidence and expected failure semantics.

A bare imperative sentence is not a valid executable operation. It may be retained as descriptive text, but cannot authorize execution.

## 6. Dense notation safety rules

- No implicit wildcard permissions.
- No implicit network access.
- No implicit secret interpolation.
- No implicit retries.
- No implicit parallelization.
- No implicit promotion.
- Unknown values remain unknown.
- Side effects require explicit effect and policy declarations.
- Parser output must retain source spans for audit.

## 7. Adoption path

1. Compare these tokens with the existing Siglary registry.
2. Reserve only collision-free names through the existing governance process.
3. Publish grammar and AST mapping.
4. Add parser round-trip fixtures.
5. Verify shorthand → canonical SRM → shorthand stability.
6. Record deprecations and aliases without rewriting historical records.
