# MaxC Interoperability — Verified Capability Boundary

**Observed source:** `workspace/maxc/` and `appliedSxi/maxc/` on `master`, inspected 2026-11-13.

## Current capability

| Path | Verified capability | State |
|---|---|---|
| `workspace/maxc/src/main.rs` | MaxUp input → HTML output; Leptos target; `-t micro` bytecode output | Active CLI |
| `workspace/maxc/src/emitter_micro.rs` | `MAXC` header, version byte, token IDs, LEB128 lengths, serialized AST nodes | Implemented emitter |
| `workspace/maxc/src/reverse.rs` | HTML DOM → MaxUp text through `scraper` and `ego-tree` | Reverse module present |
| `workspace/maxc/src/main.rs` | Includes `mod reverse`; current argument parser exposes the forward compile routes | CLI integration gap for reverse mode |
| `appliedSxi/maxc/src_prototype_bidir/main.rs` | Prototype `--reverse` flag and HTML → MaxUp call | Prototype |
| `appliedSxi/maxc/CHANGELOG.md` | Records v0.2.0 reverse-transpiler and v0.3.0 micro-bytecode milestones | Historical release notes |

## HTML ↔ Markdown verdict

**MaxC currently qualifies as a MaxUp ↔ HTML compiler family with a partial HTML → MaxUp reverse path. HTML ↔ Markdown conversion remains a separate adapter capability.**

The active workspace source currently centers on MaxUp parsing and HTML/Leptos/bytecode emission. A Markdown parser, Markdown AST, CommonMark/GFM renderer, and Markdown output target belong in a sibling adapter. The `.maxc` format stores serialized MaxUp AST bytecode.

## Recommended parallel architecture

1. Preserve MaxUp as its own DSL and keep its AST/bytecode contract stable.
2. Add a Markdown adapter as a sibling package or backend using a standards-based CommonMark/GFM parser and renderer.
3. Normalize HTML and Markdown into a typed canonical document IR with headings, paragraphs, links, images, lists, tables, code blocks, frontmatter, and source provenance.
4. Implement `HTML → IR → Markdown` and `Markdown → IR → HTML` as separate transforms.
5. Add round-trip fixtures for semantic structure, link destinations, code fences, tables, headings, and metadata.
6. Measure fidelity, parser coverage, output validity, and token/byte cost separately.

## DerpWiki / D3rpW1ki / Der9W¡K1

The repository's `docs/ops/AGENT-MONIKERS.md` contains `derpWiki ≈ d3π9W1K¡` as a display-moniker graduation example. The inspected source search returned that moniker reference. Current repository evidence establishes the display example; an application, renderer, codec, or wiki corpus remains a future implementation item.

Treat DerpWiki as an internal concept seed. A future internal codec can use a versioned visible codebook and a reversible sidecar. Keep its output out of public Agent Ready fixtures and crawler-facing pages. Public HTML/Markdown stays canonical and human-readable.
