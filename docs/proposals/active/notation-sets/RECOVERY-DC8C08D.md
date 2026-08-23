# Recovery Evaluation — `dc8c08d` / AGENTS ↔ AGENTS.hum ↔ Linguist ↔ Caveman

**Status:** research/recovery basis; implementation not yet authorized by this document alone.

## Executive finding

Commit `dc8c08d6777fd105a42b5f2cb523f5c7ed6e87d3` is an important historical implementation anchor for the Linguist/CedrLang lineage. Its commit message identifies an O(N), line-by-line CedrLang v2 compiler/decompiler with strict casing preservation, Grimoire mapping, formatting/number/path/decimal handling, bold/emphasis protection, and comprehensive `tests/test_cedrlang.py` coverage.

The commit also contains an `AGENTS.md` implementation and a documented performance/security learning: compile regexes once, protect Markdown structure and technical identifiers with temporary placeholders, then restore them after dictionary-based symbolic translation. This is evidence that the intended system was already treating agent documentation as a translated/projection surface rather than ordinary prose.

A later merge, `ea2a2f8e4500fe7df6270fba1514036a439b1217` (PR #196), explicitly records the milestone as **O(N) single-pass compiler + `AGENTS.hum.md` round-trip**. Therefore `AGENTS.hum.md` round-trip is verified historical evidence. The current `master` `AGENTS.hum.md` is present but its content currently mirrors `AGENTS.md`; that is a recovery signal, not proof that the historical round-trip implementation remains integrated.

## Caveman lineage

The repo also contains an explicit historical Caveman mapping. Commit `06af26e59efb5ea2a2beeb23b1da32c0f57875e1` describes cached pre-sorted mappings, globally pre-compiled regex patterns, emerging-technology procurement mappings, and a **6-line caveman compression function**, with full pytest verification.

Earlier ecosystem-mapping commit `320c73beb9eaf834acb3efebcec8aeddbd44e6d7` adds `workspace/CAVEMAN_INDEX.md`, `workspace/SYSTEM_MAP.md`, and the broader `workspace/llm_map/*` family to the root README navigation, while noting role-based selection code was already in development and needed refinement, maintenance, integration, and optimization.

This establishes Caveman as an index/compression lineage component, not merely a stylistic alias.

## `70%` feedback-loop claim

The requested “70% feedback loop” / “INDEX Taxonomy mapper” reference has **not yet been independently located in the GitHub commit search performed for this recovery pass**. It must therefore remain a **provenance lead**, not a fact asserted by the proposal.

Recovery search should target, in order:

1. Linguist issue/PR bodies and comments containing `70%`, `taxonomy`, `INDEX`, `mapper`, `feedback`, `AGENTS.hum.md`, and `Caveman`.
2. `.jules/Linguist.md` and adjacent Jules learning logs.
3. historical `README.md`, `AGENTS.md`, `AGENTS.hum.md`, `CAVEMAN_INDEX.md`, and mapper/index artifacts.
4. commit ancestry around #196, #208, #218, #228 and their associated branches.
5. exported session/provenance sources when Git history alone is insufficient.

## Layered reintegration target

The recovered capability should be rebuilt as a layered projection system:

```text
                 canonical semantic record
                          │
                 notation / lexicon
                          │
                   INDEX taxonomy
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
          CONCEPT       POINTER      ALIAS
              │           │           │
              └───────────┼───────────┘
                          ▼
                  relationship graph
                          │
                    canonical IR
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
         AGENTS.md   AGENTS.hum.md   ICM/README
             │            │            │
             └──────┬─────┘            │
                    ▼                  ▼
              CedrLang/Linguist     other views
                    │
                    ▼
              Caveman/Grimoire
              compression codecs
```

The canonical semantic record must remain authoritative. `AGENTS.md`, `AGENTS.hum.md`, ICM, README, and compressed forms are projections/views and must not independently mutate the semantic registry.

## Recovery requirements

- Recover historical implementation by provenance, not copy/paste reconstruction.
- Preserve round-trip invariants before optimization.
- Protect code fences, URLs, HTML, filenames, decimals, paths, and formatting markers during translation.
- Keep regex compilation and static mapping preparation outside per-line hot loops.
- Separate canonical notation from aliases and domain-specific encodings.
- Treat Caveman and Grimoire as codecs/views unless an item explicitly promotes a representation to canonical status.
- Add tests for `AGENTS.md ↔ AGENTS.hum.md` round-trip and structural preservation.
- Record every recovered fragment's source commit/PR/path in the living lexicon provenance ledger.
- Do not reintroduce credentials, browser/session data, or other Class 3/4 artifacts during forensic recovery.

## Relationship to current NSE work

- **NSE-003:** living Index/Glossary/Dictionary model supplies the semantic registry boundary.
- **NSE-005:** typed relationships connect concepts, pointers, aliases, projections, and provenance.
- **NSE-006:** governance controls promotion from historical artifact to normative implementation.
- **NSE-007:** validation must include round-trip and structural-preservation checks.
- **NSE-009/010:** empirical measurement should evaluate compression/translation cost instead of assuming the codec is beneficial.
- **NSE-014/015:** Grimoire compression and canonical IR remain downstream of validated semantics.

## External obfuscation research

Recently starred/forked repositories related to obfuscation/obfuscate/obfuscated work may provide useful patterns for representation boundaries, reversible transforms, identifier handling, and layered encodings. They are **research inputs only** until individually inventoried and provenance-linked. No external repository should be copied into the monorepo merely because its terminology resembles Linguist/Caveman.

## Acceptance path

```text
historical fragment
  → provenance match
  → semantic classification
  → minimal fixture
  → round-trip/property tests
  → performance baseline
  → proposal item acceptance
  → small implementation PR
  → repo-gate + termux-smoke
  → projection/index integration
```

This keeps the recovery faithful to the historical system while allowing the implementation to evolve beyond `dc8c08d` rather than freezing it as a snapshot.
