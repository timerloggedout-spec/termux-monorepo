## 2026-08-02 - Regex Compilation Overhead and Strict Token Protection in Markdown Translation
**Learning:**
Regex compiling inside loop functions (e.g., executing translations on every line of an AGENTS.md file) introduces significant CPU overhead. Furthermore, naive string substitution of short 1337speak or Grimoire tokens like `h4x` or `scry` can easily corrupt inline code blocks, URLs, HTML tags, or file extensions (e.g., `.py`, `.js`). By isolating code fences, inline markdown markers, links, and filenames using temporary random UUID placeholders in a single-pass scan, we protect code syntax integrity while keeping translations extremely fast (O(N) operations).

**Action:**
Always compile regex patterns once globally. Isolate structural markdown formatting and technical identifiers (decimals, filenames) first, replacing them with unique, non-translatable placeholders before performing dictionary-based symbolic/1337speak translations, then restore them in a single final pass.
