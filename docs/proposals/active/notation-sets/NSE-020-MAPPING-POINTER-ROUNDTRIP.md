# NSE-020 — Mapping Pointer Index and 100% Lossless Round-Trip

## Intent

Make the Linguist/CedrLang compression stack explicitly reversible across every enabled layer. The phase surface is a view; the canonical semantic representation remains the source of truth.

## Provenance

- #154 — sparse randomized 1337 substitution / 70% initial phase.
- `dc8c08d` — CedrLang v2 recovery anchor.
- #196 — O(N) single-pass CedrLang v2 + `AGENTS.hum.md` round-trip milestone.
- #309 / #182 — Grimoire/compression lineage.
- #320 / NSE-001..019 — notation, living lexicon, codec and evolution substrate.
- `archwiz/pointer_index.py` and `cli-synthegration/synthegration_index.py` — existing pointer/hash infrastructure.

## Contract

Every layer must expose:

- encoder;
- decoder;
- versioned mapping/codebook identifier;
- source hash;
- output hash;
- mapping hash/pointer;
- provenance/lifecycle metadata;
- exact round-trip test.

For source `x` and layer `L`:

`decode_L(encode_L(x), mapping_L) == x`

No decoder may guess ambiguous original characters from a compact surface.

## Mapping Pointer Index

`archwiz/mapping_pointer_index.py` defines `mapping-pointer-index/v1`. It records hashes and relationships without committing source payloads or secrets. The private implementation may encrypt the mapping payload, but encryption keys remain external to git.

## Layer sequence

`human → canonical IR → canonical mapping → phase surface → pointer/mapping sidecar → transport/storage → verify → reverse → canonical decompile → human`

## Acceptance gates

- exact byte/hash equality;
- protected Markdown/code/URL/path/filename/numeric spans;
- deterministic seeded forensic reproduction;
- 0/70/100% phase tests;
- pointer/mapping drift fails closed;
- cross-layer fixtures;
- no credentials, tokens, session stores, or private mapping payloads committed;
- `repo-gate` + `termux-smoke` before executable integration is promoted.

## Follow-on

Recover and integrate `AGENTS.md` ↔ `AGENTS.hum.md`, INDEX Taxonomy, Concept/Pointer/Alias/Relationship indexes, Caveman-Micro, Grimoire, ICM and README projections incrementally. Each recovered historical behavior gets a compatibility fixture before becoming canonical.
