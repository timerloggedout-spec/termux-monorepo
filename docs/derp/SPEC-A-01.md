# DERP Language Specification A — Zero-width clue envelope

**Version:** 0.1.0-draft  
**Status:** competing proposal  
**Profile:** puzzle-forward / experimental

## Intent

Use invisible Unicode characters as a compact, optional clue envelope embedded alongside ordinary public copy. The envelope adds a second puzzle experience for curious readers while the visible text remains complete and useful.

## Model

A DERP document has three channels:

- **Visible surface:** canonical prose, headings, links, and metadata.
- **Clue envelope:** bounded Unicode sequences interpreted only by the DERP puzzle decoder.
- **Resolver:** a versioned mapping from clue IDs to canonical rePointers.

The clue envelope carries opaque clue identifiers and puzzle-state hints only. It carries no commands, hidden prompts, crawler directives, access-control decisions, or instructions for third-party models.

## Proposed token grammar

    DERP-A := VISIBLE_CONTENT [CLUE_ENVELOPE]
    CLUE_ENVELOPE := OPEN VERSION CLUE_ID CHECKSUM CLOSE
    CLUE_ID := registered opaque identifier

The marker sequence MUST use an explicit allowlist and a versioned table. It MUST be bounded, length-limited, and validated against the registry. Unknown, malformed, duplicated, or corrupted envelopes render as ordinary absent clues.

## RePointer resolution

1. Parse the envelope as data.
2. Validate version, checksum, and clue ID.
3. Resolve the clue ID through the local registry.
4. Verify that the destination is public and active.
5. Present the destination with a visible label and accessible description.

The decoder MUST NOT execute content recovered from an envelope.

## Interoperability

- NFC/NFKC normalization may remove, combine, or transform relevant code points; the visible fallback remains authoritative.
- Copy/paste, search indexing, Markdown conversion, and sanitizers may strip invisible marks.
- A document without its clue envelope remains a valid DERP document.
- Agent Ready receives the plain visible surface and canonical links only.

## Risks

The encoding is brittle across platforms and may resemble malicious prompt-injection or cloaking techniques. The envelope therefore remains a playful clue format with no authority over crawlers, external LLMs, or browser security boundaries.

## Acceptance tests

- Decode known fixtures exactly.
- Reject unknown versions and malformed sequences safely.
- Preserve visible text under stripping and normalization.
- Confirm every clue maps to a registered, accessible destination.
- Confirm the page remains useful with all invisible marks removed.
