# CEDRlang, Grimoire, and Local A2A Contract

## Purpose

**CEDRlang** is the repository’s deterministic, non-executing format for compact agent instruction records. **Grimoire** is the optional symbolic vocabulary layer used by an authorized mapper. The codec does not execute commands, edit files, invoke CEDARscript, call a network service, start a workflow, or use a local pointer registry.

> CEDRlang is a compact representation protocol, not encryption, authentication, authorization, or a security boundary.

A public symbolic representation may be non-self-describing, but it can only be reconstructed by an authorized mapper holder. The public repository includes no private mapper, key, token, or decoded private mapping. The only mapper used by tests is synthetic and deliberately non-sensitive.

## Canonical Source and Generated Forms

The canonical intermediate record (CIR) is the source of truth. It is normalized and serialized deterministically before hashing. Agent documents must remain readable canonical material until a separate approved migration creates deterministic machine projections. The root `AGENTS.md`, its human companion, `CLAUDE.md`, ICM entry points, and the public README are **not** rewritten by this initial foundation.

| CIR field | Type | Compression eligibility |
|---|---|---|
| `schema_version` and `document_id` | Stable identifiers | Excluded |
| `purpose` | Text | Eligible |
| `directives` | Ordered text list | Eligible |
| `constraints` | Ordered text list | Excluded to keep governance and safety boundaries plainly visible |
| `inputs` and `outputs` | Ordered text lists | Eligible |
| `provenance` | Text | Eligible |

The canonical SHA-256 digest is calculated over fixed-key JSON after Unicode NFC and line-ending normalization. A decoder must reject unsupported versions, mapper mismatch, malformed segments, unknown handles, and digest mismatch.

## Mapper Contract

An authorized mapper has a stable ID, semantic version, public content hash, and a bijective `forward`/`reverse` relation. Every normalized source token maps to one symbolic handle and every handle maps back to one source token. A mapper collision is a hard error, not a best-effort repair.

The 70% criterion is measured as:

```text
replaced eligible tokens / total eligible tokens
```

It is a codec-coverage metric, not a claim about proprietary model tokenization, compression ratio, encryption strength, or resistance to reverse engineering. Reports record the mapper metadata, canonical digest, numerator, denominator, coverage ratio, and excluded fields. A caller may set a threshold and receive a failure when it is not met.

## Local A2A Envelope

The initial Agent2Agent contract is local validation only. An envelope carries its protocol version, message ID, sender role, recipient role, correlation ID, intent, mapper ID/version, encoded payload, canonical digest, issuance time, TTL, and one of three states: `PENDING`, `ACK`, or `NACK`.

| Control | Behavior |
|---|---|
| Version compatibility | Unknown CIR or A2A versions fail closed. |
| Integrity | Payload decoding and envelope digest must both match the canonical record. |
| Expiry | Envelopes with a passed TTL are rejected. |
| Idempotency | The same message ID and digest is an idempotent duplicate; the same ID with a different digest is a conflict. |
| State transition | Only `PENDING → ACK` and `PENDING → NACK` are permitted. |
| Size limit | Payloads above the local 64 KiB contract limit are rejected. |

No external mailbox, workflow dispatch, public transformed comment, or remote installation is part of this contract. Such integration requires a separate, accepted proposal with supply-chain review, permissions analysis, safe output design, and prompt-injection tests.

## CEDARscript and CID Separation

CEDARscript is a distinct code-analysis and transformation language with execution-capable runtimes. The repository’s `cid.py` is a pointer registry for CEDARscript command phrases. Neither surface is a CEDRlang document decoder or a private Grimoire mapper.

The implementation must maintain the following boundary:

```text
CEDRlang CIR / mapper / A2A validator
    ├── deterministic data transformation only
    ├── no subprocess, network, filesystem mutation, or execution
    └── no CID or CEDARscript dependency

CEDARscript / CID / patch router
    └── separately governed code-editing parity surface
```

## Implementation Reference

The initial implementation is `workspace/compression_sandbox/cedrlang/protocol.py`. Its focused tests are `tests/test_cedrlang_protocol.py`. Work is tracked as proposal `cedrlang-grimoire-a2a`, item `LGA-01`; later migration work must receive separately scoped work items.

## References

1. [CEDRlang / Grimoire / A2A decision record](proposals/active/cedrlang-grimoire-a2a/source.md)
2. [Linguist agent-contact inventory](reviews/linguist-177/agent-contact-inventory.md)
3. [External CEDARScript boundary](reviews/linguist-177/external-cedarscript-boundary.md)
4. [CEDARScript Editor (Python)](https://github.com/CEDARScript/cedarscript-editor-python)
