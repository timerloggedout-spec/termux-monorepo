# DERP / d3rp language proposals

**Status:** competing draft specifications · 0.1.0 · 2026-11-23  
**Decision:** pending comparative tests and owner review.

DERP is the playful public language and discovery experience for this repository. It introduces newcomers to the project's leetspeak, symbols, rePointers, wiki, and capability surfaces through an exploratory web entrance.

The design has three cooperating layers:

1. **Surface** — readable public copy, stable links, semantic HTML, Markdown, and search metadata.
2. **Play** — clues, decoys, visual transformations, invisible-character experiments, and optional puzzle paths.
3. **Resolution** — canonical rePointer registry, destination validation, and discoverable capability maps.

The public entrance teaches DERP to newcomers. Repository documentation remains the canonical source for technical meaning and capability claims.

## Competing proposals

| Proposal | Encoding | Strength | Trade-off |
|---|---|---|---|
| [SPEC-A: Zero-width clue envelope](SPEC-A-01.md) | Bounded Unicode clue sequences with visible fallbacks | Strong hidden-layer aesthetic; compact puzzle payloads | Fragile across normalization, copy/paste, indexing, and accessibility tools |
| [SPEC-B: Visible-first token grammar](SPEC-B-01.md) | Readable leet tokens and rePointer IDs; optional invisible marks as decoration | Robust indexing, debugging, accessibility, and SEO | Less cryptic; puzzle layer is more discoverable |

## Shared invariants

- Public content remains independently understandable without decoding.
- Canonical destinations resolve through a versioned registry.
- Puzzle clues remain inert data; reserve executable instructions and crawler policy for their documented, visible control surfaces.
- robots.txt expresses crawler access policy using its standard syntax.
- llms.txt and Markdown mirrors describe public content accurately.
- Agent Ready output stays plain, predictable, and free of puzzle markers.
- Treat invisible characters as experimental presentation; use documented visible control surfaces for crawler policy and agent guidance.
- Search visibility comes from useful visible content, stable URLs, semantic metadata, internal links, and valid sitemap/robots policy.
- Every clue has a visible equivalent, accessible description, and canonical destination.
- The maze reveals documented capabilities; it does not fabricate availability or permissions.

## Evaluation

Run both candidates through the same corpus and compare UTF-8 round-trip fidelity, Unicode normalization, HTML rendering, Markdown extraction, search snippet quality, screen-reader and keyboard accessibility, link resolution, stale-pointer detection, Agent Ready plain-output parity, and newcomer clue-discovery rate.

Select a candidate only after evidence is recorded in the [decision matrix](DECISION-MATRIX.md).

## Status

This branch contains proposal artifacts only; production landing pages, robots policy, llms publication, and Agent Ready configuration retain their current settings.
