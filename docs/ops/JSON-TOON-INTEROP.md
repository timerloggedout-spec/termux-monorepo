# JSON ↔ TOON interoperability

Status: additive adapter / evaluation lane. JSON remains canonical.

## Decision

Use TOON as an optional serialization view for LLM-facing payloads and
human inspection where it demonstrates a measured benefit. Do not replace
canonical .json, .jsonl, JSON Schema contracts, API payloads, ledgers,
feeds, manifests, or evidence records with .toon.

TOON encodes the JSON data model. Its strongest case is uniform arrays of
objects; deeply nested or heterogeneous structures can be larger than
compact JSON. The upstream specification is a working draft and is versioned
independently. Pin and record the implementation/spec version for every
reproducible comparison.

## Boundaries

- **JSON**: canonical storage, schema validation, API interchange, evidence
  and audit records.
- **TOON**: derived transport/prompt representation; .toon is never the
  sole durable copy of a canonical record.
- **Siglary**: governs notation classes, semantic clarity, and receipt
  discipline. TOON syntax is not a Siglary glyph/chord/operator register.
- **MaxC / MaxUp**: remain separate language/compiler projects. No direct
  parser or syntax change is implied by this adapter.
- **CedrLang / CedarIndex / CedarForge**: remain independent compression,
  glossary, and pointer systems. A short pointer is not a serialization
  format and must resolve through its authoritative registry.
- **MCP / QUE / Actions**: may consume TOON only through an explicit adapter;
  existing schemas and authority boundaries remain unchanged.

## Adapter

scripts/notation/toon_interop.py delegates encoding/decoding to the
official @toon-format/cli. It does not implement a competing TOON grammar,
download packages, invoke a shell, or change source records.

Commands (after installing the official CLI in the environment):

    python3 scripts/notation/toon_interop.py encode data.json -o data.toon
    python3 scripts/notation/toon_interop.py decode data.toon -o roundtrip.json
    python3 scripts/notation/toon_interop.py compare data.json -o comparison.json

compare performs encode → decode and checks structural equality against
the source JSON. It reports pretty/compact JSON and TOON character/UTF-8
sizes, plus o200k_base and cl100k_base token counts when tiktoken is
installed. Missing optional tokenizer support is represented by JSON nulls
and an explicit availability reason, never by an invented zero. Tokenizer
assets must be pre-cached for isolated/offline runs; tiktoken may retrieve
encoding data on first use when its cache is empty.

Set TOON_IMPLEMENTATION_VERSION and TOON_SPEC_VERSION in the evaluation
environment to bind the report to exact versions. Do not infer versions from
a mutable package tag.

## Comparison protocol

Compare the same canonical payload in three representations:

1. pretty JSON (2-space indent);
2. compact JSON (minified);
3. TOON (official encoder, strict decoder).

Use structural cohorts, not one cherry-picked example:

- uniform arrays of objects;
- primitive arrays;
- mixed/heterogeneous arrays;
- nested uniform objects;
- deeply nested objects;
- empty/null/boolean/number/string edge cases;
- large integers, Unicode, escaping, delimiter collisions, and truncation.

Report characters, UTF-8 bytes, tokens per named tokenizer, round-trip
equality, encoder/decoder versions, and encode/decode runtime. The adapter
uses a bounded 60-second CLI timeout, rejects duplicate JSON keys and
non-finite host-number results, and invokes the executable without a shell. Keep model comprehension
accuracy as a separate experiment: token reduction is not evidence of
correctness or answer quality.

## Adoption gates

A payload family may opt into TOON only when:

- the official implementation passes the applicable upstream conformance
  fixtures;
- encode → decode is structurally lossless for the full family fixture set;
- exact implementation and specification versions are recorded;
- measured token savings exist against both pretty and compact JSON on the
  target tokenizer(s);
- downstream consumer tests pass;
- no Siglary principle-⑤ ambiguity or receipt-adjacency regression is found.

A failed round trip, unknown schema, stale version, or unavailable decoder
means retain JSON. No automatic .json rename, mass conversion, or
dual-source-of-truth is permitted.

## Future fit

- **Phase 1**: optional CLI adapter and local comparison harness (this PR).
- **Phase 2**: corpus benchmark over representative repository payloads,
  with privacy-safe synthetic fixtures and tokenizer-specific results.
- **Phase 3**: opt-in prompt/MCP response adapters for selected high-volume,
  uniform payloads; JSON remains the fallback and source of truth.
- **Phase 4**: evaluate MaxC/MaxUp only if a concrete consumer needs TOON
  input/output. Prefer an adapter boundary over embedding TOON grammar in
  the MaxC lexer/parser.
- **Phase 5**: consider broader adoption only after measured quality,
  compatibility, and maintenance benefits.

## Sources

- TOON specification: https://github.com/toon-format/spec
- Reference implementation: https://github.com/toon-format/toon
- Official CLI: https://github.com/toon-format/toon/tree/main/packages/cli
- Siglary standard: docs/proposals/active/notation-sets/SIGLARY-STANDARD.md
- Siglary token-cost findings: docs/proposals/active/notation-sets/SIGLARY-TOKEN-COST.md
- Existing notation inventory: docs/ops/LINGUIST-PANEL-FEED.md
