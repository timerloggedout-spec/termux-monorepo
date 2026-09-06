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

## 2026-08-27 - Trie-Structured Regex Alternation and Precomputed Casing Tables
**Learning:**
While flat regex alternations (`\b(term1|term2|...)\b`) collapse sequential `.sub()` calls into a single pass, long flat alternations with overlapping or common token prefixes (e.g., `procurement`/`procurements`, `curation`/`curations`, `emerging technology`/`emerging technologies`) cause redundant state evaluation and backtracking depth in the regex engine. Building Trie-structured regular expressions (`\b(?:p(?:r0cur3(?:s)?)|...)\b`) collapses shared prefix branches, reducing regex engine state space. Paired with precomputed casing lookup tables (`FAST_CASING_COMP` / `FAST_CASING_DECOMP`), this eliminates runtime casing string inspections (`apply_casing`/`is_capitalized`), reducing `decompile_doc` latency from 3.43ms to 2.34ms (~1.46x speedup) and `from_1337speak` latency from 36.48us to 20.64us (~1.77x speedup).

**Action:**
Construct Trie-structured prefix regexes for token dictionary matching and pre-populate casing lookup tables at module load time to maximize C-level regex traversal speed and bypass string casing inspection overhead.

## 2026-08-28 - Callback Closure Hoisting & C-String Pre-Screening in Document Processing Loops
**Learning:**
Defining substitution callback functions (`def _sub_cb...`) inside high-frequency string translation functions like `translate_text_raw` re-instantiates function objects on every single invocation pass. Hoisting callbacks to module scope (`_sub_cb_comp`, `_sub_cb_decomp`, `_from_1337_repl`) completely eliminates function object allocation overhead. Additionally, in document line loops (`compile_doc` / `decompile_doc`), pre-screening lines using fast C-string checks (`"```" in line`) before calling `.lstrip().startswith("```")` avoids unnecessary `str.strip()` string allocations. Direct inlining of the pre-compiled C Trie-regex search (`if not matcher.search(line): compiled_lines.append(line)`) in document iteration loops further bypasses function frame dispatch overhead for non-matching lines, delivering an additional ~1.10x compilation and decompilation throughput speedup across full markdown documents.

**Action:**
Always hoist regex match substitution callbacks to module scope and pre-screen document lines with fast C-string checks (`in line`) before calling line translation functions or allocating string slices in document compilation loops.

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
