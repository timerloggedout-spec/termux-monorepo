# Domain Composition Matrix — Research Database

Status: proposed / research implementation

## Why this exists

The repository already has notation sets, concept/pointer/alias indexes, integration graphs, and domain references. The domain composition matrix is a different object: a first-class, versioned research database.

It answers: given a domain, source type, target type, operation, notation, and semantic convention, is composition valid, how is it represented, what constraints apply, and what evidence supports the rule?

## Architectural position

Research sources → Domain Composition DB → validation / analysis / projections

The database is authoritative for domain-composition facts and hypotheses. It is not authoritative for generic notation definitions, source provenance, or runtime implementation merely because a row exists.

## Core entities

- domain — research/application domain or subdomain.
- entity_type — object/value/type category participating in composition.
- operation — composition operation or relation.
- notation — domain/language-scoped surface representation.
- composition_rule — typed rule connecting source and target entities through an operation.
- constraint — preconditions, associativity, identity, typing, or domain restrictions.
- evidence — provenance supporting the rule.
- projection — generated representation in another repository surface.
- status — hypothesis, candidate, validated, deprecated, rejected.
- version — schema/data evolution boundary.

## Important semantic rule

Generic composition and domain-specific composition are separate records.

- generic composition: f ; g
- Lean-specific composition: f ≫ g
- Haskell-specific bind: m >>= f

These may share a semantic relationship without being interchangeable syntax.

## Research posture

1. Capture the hypothesis.
2. Preserve source evidence.
3. Validate against examples and tests.
4. Compare competing domain conventions.
5. Promote only after review.
6. Retain historical rows instead of silently overwriting them.

## Relationship to existing work

- #320 — notation-set and relationship seed.
- #324 — proposal/research expansion.
- #175 — master/operator governance.
- #390 — production validation and proposal integration.
- docs/proposals/active/notation-sets/ — generic notation semantics.
- docs/ops/INTEGRATION-GRAPH-MATRIX.md — integration graph/matrix view.

The integration graph should consume this database rather than duplicate its domain-composition facts.

## Initial research dimensions

domain × source_entity × operation × target_entity × notation × language × validity × constraints × evidence × confidence

Future dimensions may include algebraic laws, typing systems, coercions, identity elements, associativity/precedence, serialization/codec behavior, reversible projections, ontology mappings, empirical compatibility, and model/tokenizer effects.

## 100% provenance rule

Every promoted rule requires rule_id + version + source + evidence + status + confidence + validation fixture.

## Files

- schema.sql — relational contract.
- seed.json — initial research records.
- README.md — architecture and governance.
- scripts/ci/validate_domain_composition.py — deterministic validator.
- tests/test_domain_composition_matrix.py — structural/data contract tests.

SQLite is the intended local research substrate; Postgres can become a shared service without changing the semantic contract.