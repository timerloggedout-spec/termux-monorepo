## 2026-08-02 - Regex Compilation Overhead and Strict Token Protection in Markdown Translation
**Learning:**
Regex compiling inside loop functions (e.g., executing translations on every line of an AGENTS.md file) introduces significant CPU overhead. Furthermore, naive string substitution of short 1337speak or Grimoire tokens like `h4x` or `scry` can easily corrupt inline code blocks, URLs, HTML tags, or file extensions (e.g., `.py`, `.js`). By isolating code fences, inline markdown markers, links, and filenames using temporary random UUID placeholders in a single-pass scan, we protect code syntax integrity while keeping translations extremely fast (O(N) operations).

**Action:**
Always compile regex patterns once globally. Isolate structural markdown formatting and technical identifiers (decimals, filenames) first, replacing them with unique, non-translatable placeholders before performing dictionary-based symbolic/1337speak translations, then restore them in a single final pass.

## 2026-08-03 - Compiled Caching of Dynamic Mappings and "Caveman" 6-Line Routine
**Learning:**
On-the-fly dictionary sorting and regex pattern compilation inside nested loops (e.g., executing translations for links, bold, emphasis, and raw text on every line) is a catastrophic CPU bottleneck. By caching sorted mappings globally at module load and precompiling compiled regex patterns once, we can eliminate execution overhead. Additionally, a highly dense 6-line "Caveman" function achieves maximum compression and execution speeds using these pre-compiled static sets.

**Action:**
Cache sorted mappings and compile all dynamic regex matchers globally at initialization time to avoid runtime compilation loops. Maintain compact routines like `caveman` within strict line budgets by reusing globally precompiled structures.
