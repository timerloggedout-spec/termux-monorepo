# CEDRlang / Grimoire / A2A Technical Decision Record

## Decision

CEDRlang is a **non-executing**, deterministic codec and local message-validation layer. It operates on a typed canonical intermediate record (CIR) and may use a mapper that is injected by an authorized caller. The public repository contains only a synthetic test mapper. The **Grimoire** name refers to the optional symbolic presentation layer; it is not encryption, authentication, access control, or a claim of secrecy. CEDARscript and the current CID pointer registry remain separate code-editing/parity tooling and are not called by CEDRlang.

A literal one-way transformation cannot independently yield perfect reverse translation. The accepted technical model is therefore: a public symbolic representation is non-self-describing, while an authorized mapper holder can reconstruct the normalized canonical record deterministically and verify its integrity. No private mapper is committed, logged, embedded in a generated document, or copied into a pull-request comment.

## Canonical Intermediate Record

A canonical record has the following fields: `schema_version`, `document_id`, `purpose`, `directives`, `constraints`, `inputs`, `outputs`, and `provenance`. Each field is plain text or an ordered list of plain text. Canonicalization performs Unicode NFC normalization, normalizes line endings to LF, removes trailing whitespace, rejects NUL/control characters, and serializes a fixed sorted-key JSON representation. Its SHA-256 digest is the transmission-integrity value.

## Mapper Contract

A mapper is an immutable, versioned mapping from a normalized eligible token or phrase to an unambiguous symbolic handle. It supplies `mapper_id`, semantic version, a public content hash, `forward` and `reverse` maps, and an explicit `private` custody flag. A valid mapper has unique handles and a bijective reverse map. The codec rejects collisions, unknown handles, malformed handles, cycles, invalid versions, and content hash mismatches. The implementation provides a synthetic `test-grimoire-v1` mapper only; a production mapper must arrive through an operator-approved secret-safe interface that is outside this repository.

## Coverage and 70% Target

The measurable 70% target is **not** an estimated tokenizer claim. It is `replaced_eligible_tokens / total_eligible_tokens` across the allowed CIR fields. Structural keys, schema/version fields, digests, IDs, safety constraints, and escaped protected literals are excluded from the denominator. A report includes the numerator, denominator, exclusions, mapper ID, mapper version, canonical digest, and calculated ratio. The codec can enforce a caller-selected minimum target and fails closed when the threshold is not reached.

## A2A Envelope

The local A2A envelope is a typed schema rather than arbitrary compressed prose. It carries protocol version, message ID, sender role, recipient role/capability, correlation ID, intent, payload, mapper identity, canonical digest, issuance timestamp, TTL, state, acknowledgement ID, and error code. It validates IDs, size limits, version compatibility, expiry, digest, and allowed state transitions. It categorizes duplicate message IDs as idempotent duplicates only when the canonical digest matches; a reused ID with a different digest is a conflict. The initial implementation performs no network access, no workflow dispatch, no external install, and no code modification.

## Explicit Non-Goals

The following are excluded from this proposal: migrating the root `AGENTS.md` or `README.md`; generating human or machine instruction projections; changing `.cedar/cedar_index.json`; changing `cid.py`; invoking CEDARscript, `sed`, `awk`, AST tools, or patch routers; installing MCP Agent Mail; posting transformed public content; changing GitHub Actions; and creating a private-mapper secret store. These items need separate approved work items after the canonical codec proves its constraints.

## Evidence Basis

The decision is based on the bounded graph rooted at PR #177, all-state title inventory, local source inventory, and the operator scope guidance for the dirty Linguist PRs. It preserves the valid requirements for deterministic translation and A2A protocol development while correcting the current scope mix between a document translator and an execution-capable code-editing system.
