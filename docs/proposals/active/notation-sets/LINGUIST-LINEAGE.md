# Linguist Lineage — Notation Sets / Living Lexicon

This document is a provenance map, not a new proposal and not an implementation authorization.

## Purpose

The `notation-sets-evolution` proposal is the semantic specification/research substrate for an existing Linguist/CEDRlang/Grimoire lineage. It must preserve the distinction between historical implementation evidence, governed successor work, projection surfaces, and current research hypotheses.

## Lineage map

```text
Linguist
├── historical implementation evidence
│   ├── #126  CedrLang agentic communication compiler
│   ├── #154  CedrLang v2 / Grimoire / AGENTS.hum.md
│   ├── #177  document token-compression protocol
│   ├── #196  CedrLang v2 compilation
│   ├── #208  compile optimization + procurement mappings
│   ├── #218  single-pass CedrLang optimization
│   └── #228  fast-path term search
│
├── governed reconciliation
│   └── #274  Linguist integration tracker
│       └── #275 bounded CEDRlang + local A2A successor
│
├── projection / contact surfaces
│   └── #304 human/machine contact-document projections
│
└── semantic research/specification
    └── #320 Notation Sets
        └── notation-sets-evolution
            ├── NSE-001..008 normative vocabulary/governance substrate
            └── NSE-009..018 measurement + codec/compression research
```

## Disposition classes

| Artifact | Disposition | Relationship |
|---|---|---|
| #126, #196, #208, #218, #228 | historical implementation evidence | Useful empirical/technical lineage; do not imply current authority by age alone. |
| #154, #177 | legacy/broad evidence roots | Preserve for provenance and lessons; not automatically merge sources. |
| #274 | governed reconciliation tracker | Records the Linguist integration boundary. |
| #275 | bounded successor implementation | Current governed CEDRlang/local-A2A implementation candidate in the lineage. |
| #304 | projection implementation | Human/machine contact-document projection surface and public bootstrap lexicon boundary. |
| #320 | relationship/research seed | Supplies notation sets and cross-domain semantic distinctions. |
| NSE-001..008 | specification | Canonical taxonomy, semantic preservation, living lexicon, evolution, relationships, governance, validation, ledger. |
| NSE-009..018 | research program | Measurement and codec/compression hypotheses requiring empirical validation. |

## Architectural boundary

```text
canonical source / semantic record
             ↓
notation + living lexicon
             ↓
canonical IR
             ↓
validated rendering / codec
             ↓
AGENTS / CLAUDE / README / ICM projections
```

The living lexicon does not replace existing indexes or #304 projections. It supplies stable semantic keys, provenance, typed relationships, and lifecycle state so those surfaces can remain synchronized without becoming competing authorities.

## Evidence rule

Historical PR descriptions are evidence of what was proposed or implemented at the time. They are not, by themselves, proof that the implementation remains current, authoritative, secure, or mergeable. Current governance and repository validation determine execution authority.

## Connections

- #320 — notation seed and relationship hub
- #309 / #182 — Grimoire/compression lineage
- #274 / #275 — governed Linguist/CEDRlang reconciliation
- #304 — projection/contact-doc implementation
- #175 — operator/master gate
- `docs/proposals/active/notation-sets/ITEMS.md` — NSE specification/research items
- `docs/proposals/active/notation-sets/MANIFEST.md` — proposal lifecycle and review state

## Evolution rule

New Linguist-related issues or PRs should be classified here before being promoted into NSE work. A new artifact may extend the lineage without automatically becoming canonical. Semantic promotion requires provenance, classification, review disposition, and—when executable—its own accepted item and required repository gates.
