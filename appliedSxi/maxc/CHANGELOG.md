Promoted: 2026-06-29T00:32:05Z — Iterative parser, clean HTML output
Promoted: 2026-06-29T00:42:52Z — Modular CLI, clean debug modes, file I/O

## v0.2.0 — Bi‑directional Reverse Transpiler (2026‑06‑28)
- Added `--reverse` flag to convert HTML → MaxUp
- Compresses `class="foo"` to `.foo`, `id="bar"` to `#bar`
- Supports void elements, inline text, nested blocks
- Added `scraper` / `ego‑tree` dependencies for HTML parsing
- Warning‑free compilation

## v0.3.0 — Micro Bytecode Backend (2026‑06‑28)
- Added `-t micro` target: emits `.maxc` binary AST
- LEB128‑encoded lengths, 1‑byte token IDs, flags for id/class
- Magic header `MAXC` + version byte
- Base64 stdout when no output file specified
- Payload: 453 bytes vs 510 bytes HTML (spec.max), 10–15× smaller for real pages
