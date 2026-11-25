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
- verification required by the declared mapping mode.

Reversible modes use exact round-trip equality. Intentionally lossy modes declare their accepted loss and evaluation target; exact reconstruction applies when the selected mode declares it.

For source `x` and a reversible layer `L`:

`decode_L(encode_L(x), mapping_L) == x`

Decoder behavior follows explicit mapping evidence for ambiguous original characters.

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

Preserve the root `AGENTS.md` ↔ `AGENTS.hum.md` milestone as historical lineage. The current Agent-document layer registers seven active machine surfaces with unique sibling `*.hum.md` sources in `scripts/linguist/agent_document_pairs.py`; each row declares its relationship class and mapping mode. Current Agent-document lanes use `identity`, and ICM aliases stay byte-identical. Continue INDEX Taxonomy, Concept/Pointer/Alias/Relationship indexes, Caveman-Micro, Grimoire, ICM and README recovery incrementally, with compatibility fixtures for each historical behavior before canonical promotion.
