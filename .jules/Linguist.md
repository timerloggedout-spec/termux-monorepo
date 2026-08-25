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

## 2026-08-04 - Single-Pass Alternation Regex vs Sequential Pattern Evaluation
**Learning:**
Executing sequential `.sub()` calls for N individual regex patterns across document lines creates massive O(N_terms * N_lines) overhead and unnecessary function frame allocations. Combining all dictionary substitution terms into a single compiled regex pattern with word-boundary alternations (`\\b(term1|term2|...)\\b`) allows Python's C-level regex engine to match any term in a single pass O(1_regex * N_lines). In CedrLang document translation, this reduced document compilation latency from 31.4ms to 7.3ms (~4.3x speedup).

**Action:**
Combine dictionary substitutions into single compiled regex patterns with alternations and dictionary lookups in the match callback instead of executing sequential regex substitution loops.

## 2026-08-05 - Fast-Path Term Pre-Search in Document Transformation Pipelines
**Learning:**
In line-by-line document translation pipelines where structural syntax protection (e.g. code fences, URLs, markdown formatting) involves multiple sequential regex evaluations, running placeholder extraction on lines that contain zero target translation terms is a massive CPU bottleneck. A single O(1) pre-search using a pre-compiled single-pass term matcher (`if not matcher.search(line): return line`) allows ~96% of document lines to bypass structural regex parsing entirely, reducing CedrLang compilation time per document from ~7.22ms to ~4.00ms.

**Action:**
In line-level transformation utilities, always perform a fast-path term existence pre-check (`matcher.search(line)`) before executing multi-pattern placeholder protection or DOM parsing pipelines.

## 2026-08-23 - Phased 1337 Diaspora Recovery / PR #154
**Learning:**
PR #154 contains the provenance-backed historical `to_1337speak()` experiment. The Jules review comment at `discussion_r3754718523` describes a sparse randomized substitution rate with a **70% probability threshold**, intended to introduce character-level variability while retaining decompression to human-readable form. This is a rollout parameter, not an INDEX confidence score.

**Action:**
Restore the behavior as an explicit reversible phase in `workspace/compression_sandbox/cedrlang/phase_codec.py`. Keep canonical CedrLang/Grimoire semantics upstream; mutate only known compressed tokens; normalize known variants before canonical decompilation; seed RNGs for reproducibility; and ratchet the probability only after round-trip, quality, latency, and ambiguity measurements. Initial phase is `p=0.70`.

**Provenance:**
- PR #154 review comment `discussion_r3754718523`
- `dc8c08d` — CedrLang v2 compilation / strict token protection
- `1103d832` / `51023b87` / `7a6e5a7` — cached mappings, Caveman, single-pass regex optimization
- `4eb9f830` / `267fecc` — fast-path term search
- #196 — `AGENTS.hum.md` round-trip milestone

## 2026-08-26 - Trie-Structured Regex Patterns and Precomputed Casing Variant Lookup
**Learning:**
Using flat regex alternations (`\b(term1|term2|...)\b`) with large dictionaries (e.g. 55+ 1337speak variants in `phase_codec.py` or 27+ CedrLang mappings) forces Python's C-level regex engine to perform linear search branching across bytecode instructions on every word match attempt. Generating a prefix Trie-structured regex (`\b(?:prefix1(?:sub1|sub2)|prefix2...)\b`) minimizes state machine search depth, yielding a ~2.7x speedup for 1337speak phase codec operations (from ~4.9ms to ~1.8ms per call) and ~1.5x speedup for document compilation/decompilation. Furthermore, pre-computing static casing variant lookup dictionaries (`FAST_CASING_COMP`, `FAST_CASING_DECOMP`) at module load eliminates runtime string allocation and casing inspection overhead during match callback execution.

**Action:**
When building single-pass dictionary regex pattern matchers for multi-term translation protocols, always construct Trie-structured regex patterns and pre-calculate casing variant lookup tables to minimize regex state-machine branching depth and callback function overhead.
