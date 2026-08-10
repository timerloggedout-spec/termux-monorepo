# Linguist's Performance Journal

Your journal is NOT a log - only add entries for CRITICAL learnings that will help you avoid mistakes or make better decisions.

## 2026-08-10 - O(N) Regex Translation with Placeholder Protections for Markdown
**Learning:**
Translating rich formats like markdown into custom formats (e.g., 1337speak) can corrupt functional elements (code blocks, hyperlinks, formatting punctuation). Attempting to parse markdown line-by-line or with complex context-free parsing is slow and complex.
Instead, employing a content-agnostic regex placeholder mask during translation maps functional constructs to stable IDs (like `__PLACEHOLDER_N__`) first, executes a single-pass regex compilation substitution for 1337speak/symbols, and then restores placeholders. This secures O(N) time complexity and ensures syntax preservation without regressions.

**Action:**
When developing compression translators, always use placeholder protection masks for structural syntax before executing general token or letter substitutions.
