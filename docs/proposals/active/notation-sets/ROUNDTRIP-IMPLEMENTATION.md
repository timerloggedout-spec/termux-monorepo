# Round-Trip Implementation Plan — Linguist / CedrLang

## Status

**Master-first recovery slice implemented.** Commit `5bc480a00651b40678c78f0f44df0f6f787a32b0` restores the phase codec as a reversible, testable layer.

## Historical anchor

PR #154 records a sparse randomized `to_1337speak()` substitution with a 70% probability threshold and the requirement that compiled output remain de-compressible to human-readable form. The 70% value is an intentional initial rollout phase, not a claim of optimality.

The later #196 milestone records CedrLang v2 as an O(N) single-pass compiler with `AGENTS.hum.md` round-trip. The current recovery therefore preserves the historical surface codec while keeping canonical compilation/decompilation authoritative.

## Layer contract

```text
human source
   ↓
canonical semantic/document representation
   ↓
CedrLang / Grimoire canonical mapping
   ↓
phase surface codec (70% initial diaspora)
   ↓
Mapping Pointer Index / sidecar
   ↓
transport or storage
   ↓
verify hashes + mapping pointers
   ↓
reverse phase codec
   ↓
canonical decompiler
   ↓
human source
```

### Mode-specific round-trip contract

Each enabled lane declares its output mode and equivalence rule. Identity lanes require byte/hash equality, and reversible lanes require `decode_L(encode_L(x), mapping_L) == x`. Intentionally lossy modes declare their accepted loss and evaluation target, then follow that mode-specific contract. The current 70% phase codec mutates registered canonical tokens; the Agent-document lanes declare `identity`. The `1337_$934k` README mention remains historical PR #1642 Grimoire provenance.

Exact reconstruction applies when the selected mode declares reversibility or an exact source mapping. Decoder behavior follows explicit mapping evidence for ambiguous 1337 digits.

## Implemented

- `workspace/compression_sandbox/cedrlang/phase_codec.py`
  - historical 70% phase value;
  - seeded deterministic reproduction;
  - legacy `to_1337speak()` / `from_1337speak()` compatibility;
  - `encode_lossless()` / `decode_lossless()` exact sidecar mode;
  - source/output SHA-256 assertions;
  - fail-closed mapping-pointer validation.
- `archwiz/mapping_pointer_index.py`
  - schema `mapping-pointer-index/v1`;
  - source/encoded/mapping hashes;
  - layer + parent relationships;
  - no source secrets or encryption keys stored in git.
- `tests/test_phase_codec.py`
  - 0%, 70%, and 100% phase round trips;
  - drift rejection;
  - protected technical text behavior.

## Next recovery layers

1. Maintain the seven active Agent machine-to-human pairs in `scripts/linguist/agent_document_pairs.py`; each lane declares its FLY-006 relationship class and mapping mode. Current Agent-document lanes use `identity`; preserve each ICM Claude/AGENTS alias byte-for-byte and keep the earlier root `AGENTS.md` projection as historical lineage.
2. Recover the INDEX Taxonomy mapper and connect Concept / Pointer / Alias / Relationship indexes.
3. Reconcile `archwiz/pointer_index.py` with `cli-synthegration/synthegration_index.py` pointer/hash formats; retain full hashes as the canonical identity and short hashes only as display aliases.
4. Recover Caveman-Micro/Caveman fork behavior and benchmark against the existing Grimoire/CedrLang path.
5. Add ICM + README + code-comment projection checks so layer documentation cannot silently drift.
6. Add multi-layer fixtures proving exact recovery after every enabled codec/serialization/compression boundary.
7. Add authenticated encryption only for the private Mapping Pointer Index transport/storage layer using a managed secret; never commit keys or treat encryption as compression.

## 70% rollout rule

`0.70` is the initial diaspora phase. Increasing it is an operational rollout decision. Every increment must pass exact round-trip, semantic/task equivalence, technical-identifier protection, latency, and ambiguity checks. The canonical source and canonical IR remain unchanged by rollout percentage.

## Security boundary

The public repository may contain schemas, hashes, fixtures, and deterministic codec behavior. Private mapping payloads, session exports, credentials, WAF/AWS tokens, and encryption keys are outside this source-of-truth layer and must not be copied into public documentation or committed artifacts.
