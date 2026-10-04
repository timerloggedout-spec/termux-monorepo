# Context Relationship Pointer Fabric

Status: proposed implementation contract on `feat/context-relationship-rust-acceleration`

## Purpose

Unify the existing forward pointer records, reverse content-hash index, Context Relationship Graph (CRG), and optional Rust acceleration into one metadata-only pointer fabric.

The Rust layer is a computation plane. It is not a second graph authority.

## Existing directions

There are complementary pointer directions:

```text
forward:
(session, message, block, span) -> content identity

reverse:
content identity -> source/session/location references

relationship:
file/symbol -> GitHub commit/PR/issue/review/timeline relationships

structural:
content identity -> Merkle fragment -> ordered child identities
```

The fabric composes these directions without copying source bodies into the CRG.

## Identity contract

Canonical identity MUST be a full BLAKE3-256 digest.

Human/LLM-facing compact references MAY use the first 128 bits encoded as unpadded base64url.

The compact reference is a locator/display token, never the canonical identity. A store MUST retain the full digest and MUST verify it before treating a compact reference as authoritative.

Do not use 48-bit-only identifiers as canonical identity. At 1,000,000 independent identities, the birthday-collision probability for a 48-bit namespace is approximately 0.1774778%. A 128-bit namespace at 1,000,000,000 identities is approximately 1.47e-21.

## Merkle structure

For nested fragments, the parent digest SHOULD be computed from a domain-separated encoding of:

1. node kind;
2. canonical semantic payload;
3. ordered child full digests.

Child IDs supplied by callers are not sufficient to establish Merkle semantics unless they are themselves verified content identities.

Tree edges describe containment. Match/dedup edges remain separate.

Raw memory pointers MUST NOT cross a persistence or synchronization boundary.

## Termux edge plane

Termux is the local high-performance indexing plane:

```text
local sessions / exports / source
            |
            v
      bounded collector
            |
            v
     Rust AArch64 hot path
       |       |       |
       v       v       v
    hashing  frequency  cost
       |       |       |
       +-------+-------+
               |
               v
       metadata delta
               |
               v
       validation receipt
```

The Termux database remains local/private. Only an explicitly projected metadata delta crosses the synchronization boundary.

The projection MUST exclude prompts, completions, secrets, credentials, tokens, browser state, and arbitrary session bodies.

## GitHub Actions verification plane

GitHub Actions is the reproducible validation plane:

```text
Termux metadata delta
        |
        v
schema + digest validation
        |
        +--> Rust fmt/check/test/clippy
        |
        +--> Python CRG contract tests
        |
        +--> provenance / scope checks
        |
        v
validated evidence
```

CI validates the computation; it does not blindly trust a Termux database.

## Existing index integration

Do not replace the existing pointer index.

Instead:

```text
Pointer
  |
  +--> content_hash
          |
          +--> reverse pointer index
          |
          +--> Merkle fragment identity
          |
          +--> CRG relationships
          |
          +--> provenance/history
```

This allows the existing reverse index to become the lookup surface over a stronger content identity substrate.

## Bounded operating loop

The collaborator's bounded loop model is adopted as an operational contract:

1. **Observe** — read fresh state and record the evidence boundary.
2. **Choose** — select the highest-value in-scope action from explicit criteria.
3. **Act** — perform one bounded, reversible change.
4. **Verify** — run the same acceptance checks under recorded conditions.
5. **Record** — persist action, evidence, outcome, and remaining work.
6. **Repeat or stop** — continue only when measurable progress exists.

For repository stewardship this composes with:

```text
RECON
 -> PLAN / MEASURE
 -> IMPLEMENT / ACT
 -> COMMIT
 -> WAIT
 -> WATCH
 -> VALIDATE
 -> RE-FETCH
 -> COMPARE
 -> CLASSIFY
 -> RECORD
 -> REPEAT
```

Queued or in-progress status is not success.

Terminal states are explicit: `success`, `clean no-op`, `blocked`, `approval-required`, `exhausted`, or `stagnated`.

A loop definition does not itself authorize scheduling, production mutation, destructive action, or external messaging.

## Pointer economics

The frequency/cost model remains observational:

```text
savings = (f - 1) * S - f * P - H
```

where:

- `f` = observed repetition frequency;
- `S` = rendered bytes represented by one repeated fragment;
- `P` = pointer/reference bytes;
- `H` = per-node metadata/management overhead.

A pointer candidate is beneficial only when measured savings are positive under the recorded representation.

Zipf alpha MAY be recorded as a distribution diagnostic. It MUST NOT be used as a correctness gate.

## Polyglot boundary

Language-specific analyzers are providers, not authorities.

The stable boundary is a bounded, typed stream such as JSONL or a future versioned binary protocol:

```text
Python orchestration
      |
      +--> Rust structural/content hot path
      +--> Tree-sitter / language AST providers
      +--> Lizard / Radon complexity providers
      +--> numerical kernels where justified
      +--> Lua policy modules where justified
```

Providers MUST return versioned measurements with provenance. Raw provider output does not automatically become CRG truth.

## Security and authority

- Metadata-only by default.
- Full source bodies stay outside the relationship graph unless separately authorized by an existing source store.
- No raw pointers in persisted records.
- No secrets in telemetry or synchronization artifacts.
- No second graph datastore.
- No implicit merge or promotion.
- Candidate relationships remain candidates until directly evidenced.

## Acceptance criteria

The implementation is ready for promotion when:

- Rust canonical/full-hash and compact-ref tests pass;
- nested child-digest semantics are covered by deterministic fixtures;
- Python adapter fallback/required modes pass;
- source collection remains the semantic authority;
- the pointer index can resolve both forward and reverse directions;
- synchronization artifacts contain only permitted metadata;
- CI and Termux outputs agree on deterministic fixtures;
- provenance distinguishes COMMITTED, EXECUTED, VALIDATED, and PROMOTED states.

## Non-goals

This document does not authorize:

- automatic production deployment;
- automatic PR merge;
- replacing the existing CRG datastore;
- exporting private session bodies;
- treating compact references as collision-free canonical IDs;
- using Zipf statistics as a correctness policy;
- arbitrary shell execution of language providers.
