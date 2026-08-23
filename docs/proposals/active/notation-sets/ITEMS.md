# ITEMS — notation-sets-evolution

## NSE-001 — Canonical notation taxonomy

Define a machine-readable-friendly taxonomy distinguishing:

1. **Canonical** — notation normative for the originating mathematical/computational domain.
2. **Alias** — semantically equivalent shorthand accepted by the same domain or repository convention.
3. **Cross-domain analogue** — structurally parallel notation whose meaning must not be assumed identical.
4. **Domain-specific syntax** — notation whose semantics depend on a particular language, framework, or calculus.
5. **Deprecated/legacy** — retained for search and migration but not emitted by new tooling.

**Initial seed from #320:** morphism `f: A → B`; composition `g ∘ f`; identity `id_A`; functor `F: C → D`; natural transformation `α: F ⇒ G`; opposite category `C^op`; product/coproduct duality; exponential `Y^X`.

## NSE-002 — Grimoire compression contract

Specify how notation tokens participate in #309/#182 compression without collapsing distinct semantics. Compression MUST preserve the semantic category, directionality, composition order, identity behavior, and domain scope needed to reconstruct the expanded form.

## NSE-003 — Living index/glossary/dictionary

Create a continuously regenerated vocabulary layer that records, for every term or symbol:

- canonical key and display form;
- definition;
- domain/category;
- aliases and observed variants;
- semantic relations and duals;
- source issues, proposals, commits, and implementation paths;
- confidence/provenance;
- lifecycle state;
- first-seen and last-verified timestamps;
- replacement/deprecation links.

The registry should cross-link to existing `archwiz/CONCEPT_INDEX.md`, `archwiz/POINTER_INDEX.md`, `archwiz/TOOL_INDEX.md`, `archwiz/METHODOLOGY_INDEX.md`, `workspace/llm_map/ALIAS_INDEX.md`, `workspace/llm_map/INDEX_OVERVIEW.md`, and `docs/icm/objects/knowledge/context-relationship-index.md` rather than creating an isolated competing index.

## NSE-004 — Continuous research and expansion loop

Establish a repeatable research loop:

`discover → normalize → classify → cross-check → relate → index → validate → observe → revise → publish`

Inputs include new issues, proposal sources, implementation changes, agent observations, mathematical/computational references, and repository terminology. Every expansion records provenance and avoids silently promoting an analogy into a canonical definition.

## NSE-005 — Context-relationship integration

Use the proposal's notation keys as stable semantic anchors for context-relationship mapping. A notation entry can point to issues, proposals, branches, files, tools, and related concepts; it does not replace those source artifacts.

## NSE-006 — Operator/CI governance coupling

Align implementation with #175's live operator rules: no force-push to master; prefer small green rebased PRs; require `repo-gate` + `termux-smoke`; keep changes extractable; and treat the notation registry as documentation/specification until separately accepted for execution.

## NSE-007 — Validation and drift detection

Add validation for:

- duplicate canonical keys;
- alias collisions;
- malformed relations;
- missing provenance;
- broken issue/file/branch links;
- canonical-vs-domain-specific classification errors;
- stale entries whose source has materially changed;
- index entries that diverge from generated outputs.

## NSE-008 — Evolution ledger

Maintain an auditable evolution ledger for additions, reclassifications, aliases, deprecations, and semantic corrections. Changes should be attributable to a source artifact and review disposition rather than overwritten in place without history.

## NSE-009 — Language information-density baseline

Anchor the project's "language" axis on the human-linguistic baseline, kept as a **separate reference layer** from LLM tokenizer efficiency:

- Coupé et al. (2019), *Different languages, similar encoding efficiency* (Science Advances) — cross-language convergence near ~39 bits/s = Information Density × Speech Rate. Japanese: lower info/syllable, higher syllabic rate; English: denser/syllable, intermediate rate; Mandarin/Vietnamese: denser/syllable, lower rate.
- Petrov et al. (EMNLP 2023), *Do All Languages Cost the Same?* — commercial-API tokenizers over-fragment underrepresented scripts, producing unequal cost/latency/effective-context by language.
- *Language Model Tokenizers Introduce Unfairness Between Languages* — no examined tokenizer reaches broad parity across FLORES-200.
- FLORES-200 — aligned multilingual sentence corpus for holding semantic content approximately constant.
- tiktoken encodings — `cl100k_base`, `o200k_base` as reproducible tokenizer-side controls.

**Separation rule:** human communication density, encoding/tokenization parity, and LLM semantic-output efficiency are three distinct findings; surface compactness (chars/bytes) does **not** imply lower token cost (byte-BPE can fragment non-Latin scripts more aggressively).

## NSE-010 — Token-cost measurement schema

Define a versioned tensor `(language, script, content_type, concept_item, tokenizer, model, prompt, metric)` with per-item fields: `concept_id, source_language, target_language, script, translation_source, unicode_codepoints, grapheme_clusters, utf8_bytes, words, morphemes, tokenizer_name, tokenizer_encoding, token_count, bytes_per_token, tokens_per_byte, tokens_per_word, tokens_per_morpheme, relative_token_cost_en, semantic_equivalence_score, task_quality_score, latency_ms, output_tokens`.

Use aligned parallel-text design (same `concept_id` across languages); medians, quantiles, and bootstrap CIs (not averages only). Seed languages: Japanese, English, Russian, Mandarin, Korean, Arabic, Hindi, Spanish, Turkish, Finnish, Vietnamese. Content classes: plain declarative, technical/scientific, named entities/numbers/dates, code-adjacent (JSON/URLs/API names).

## NSE-011 — Adaptive Dynamic Language Mixing (ADLM) semantic codec

Treat language/representation choice as a tokenizer- and model-specific compression channel — algorithmic codec, not human code-switching:

`r*_i = argmin over r in R of [ α·tokens_T(r(s_i)) + β·ambiguity(r) + γ·decode_risk_M(r) + δ·switch_cost(r) ]`

Candidate set R: natural languages, scripts, abbreviations, symbolic forms, controlled vocabulary, JSON keys, tables, equations, domain codes. Two-layer protocol: language-neutral **canonical IR** (truth-bearing) + compiler selecting per-span encodings → **mixed input, canonical output** (e.g., English JSON) for reliable validation. Published evidence warns multilingual LLMs degrade on uncontrolled code-switched input, so token savings must be evaluated jointly with comprehension/reasoning/generation fidelity.

## NSE-012 — Context-adaptive semantic codec & layered codebooks

Optimize the **highest stable semantic unit**, not word/language alone. Codec levels: character/grapheme, phoneme/syllable, morpheme, lexeme/phrase, semantic relation, template/schema, domain concept, speaker/author style.

Conditional Zipf: estimate `P(m | c)` where `c = (model, tokenizer, domain, task, author, audience, register, repository, time)`; assign candidates `f*(m,c) = argmin over f of [ λ_t·T(f) + λ_b·B(f) + λ_a·A(f,c) + λ_q·(1−Q) + λ_s·S ]`.

Layered, versioned codebooks (each with explicit scope + retirement rules): universal, model-tokenizer, language/script, domain, repository, team/social-dialect, author/speaker-profile, session-local. This aligns with NSE-003's living glossary as the persistent, versioned semantic-definition layer; the session renderer emits disposable compact aliases.

**Hard gates:** require `Q` (task quality) and `V` (output validity) before optimizing token/byte cost; enforce round-trip semantic recovery + task-equivalence + contract-validity checks. A codec saving 18% prompt tokens but raising repair rate 10% is a net loss.

## NSE-013 — Evolutionary search & Pareto frontier

Genotype: span boundaries, candidate renderings by language/script, transliteration, glossary assignments, reordering rules, output-language/schema constraints. Fitness:

`F = w_q·Q + w_v·V + w_t·tokens + w_b·bytes + w_l·latency + w_r·repair + w_a·ambiguity`

Operators: mutate one span's language/rendering; merge neighboring spans into a single-language block; replace recurring phrases with a dictionary symbol; swap scripts/transliteration; crossover high-performing genomes with canonical-equivalence tests. Objective: `min(tokens, latency, cost)` s.t. `Q ≥ Q_min` → Pareto frontier. Report episode-level metrics (total tokens incl. output + repair, byte reduction, latency, schema validity %, task quality, semantic-recovery %, repair rate, cross-model portability).

## NSE-014 — Grimoire compression stack (#309 / #182)

Layered library stack: **zstd** (default persistent, dictionary-trained, tunable levels, streaming), **LZ4** (hot cache / latency-critical), **Brotli** (web/text distribution), **libarchive** (container compatibility), **FastCDC** (content-defined chunking for stable dedup), **xdelta3** (delta compression over snapshots), **MessagePack/CBOR** (compact typed serialization before compression), **Apache Arrow + Parquet** (columnar event/provenance logs).

Decision matrix: canonical concepts/morphisms/provenance → CBOR + zstd dict + CAS blocks; transient graph state → LZ4 + memory cache; repeated prompts/templates/citations → token/phrase IDs + zstd dict; large corpus → chunked UTF-8 + zstd + FastCDC; incremental snapshots → xdelta3 over prior snapshot + zstd; API exports → JSON at boundary + Brotli. Monorepo: codec, IR, validation, and storage contracts evolve together.

## NSE-015 — Canonical IR for category-theoretic & semantic notation

Normalize notation into a compact intermediate representation before compression (per #309/#182):

`O:<id>` (object) · `M:<src>:<tgt>:<label>` (morphism) · `COMP(<m1>,<m2>)` (composition) · `ID(<obj>)` (identity) · `F:<src-cat>:<tgt-cat>` (functor) · `NAT:<f1>:<f2>:<map>` (natural transformation).

Apply: interning (stable IDs for recurring objects/labels/functors), canonicalization (normalize aliases `g ∘ f` / `f ; g` / `f >>> g` into one IR), hash-consing (shared subgraphs), dictionary training per corpus class (math notation, NL annotations, source code, provenance), structural references (parameterized diagram templates + substitution vector), bounded delta chains with periodic checkpoints. Structural libraries: DisCoPy / Catlab.jl (semantic core), Lean Mathlib (machine-checked constraints), Rust `petgraph + serde + zstd` (performant IR), fp-ts/effect (app layer). Package layout: `grimoire-core/{ir,normalize,validate,rewrite}`, `grimoire-codec/{binary,dictionary,compression,delta,chunking}`, `grimoire-store/{cas,index,cache,snapshot}`, `grimoire-interop/{jsonld,graphml,mermaid,api}`.

## NSE-016 — Agent-native compressed communication

Agents exchange the compressed (mixed-language / symbolic / dictionary-coded) form **directly** as the communication medium; a compiler/renderer expands it into the multiple layered implementations (canonical IR → semantic validation → candidate generation → tokenizer scoring → model comprehension testing → context-aware rendering → model response → parse + validate → canonical output IR). **External information is transmuted and compressed** into the project's indexes, libraries, and diction/dictionaries on ingest: raw sources are normalized into the canonical IR, recurring semantic units are interned and assigned stable codebook entries, and only the compact surface form is carried on the hot path. The canonical IR is the truth-bearing layer; the compressed form is a disposable, context-bound view of it (see NSE-003 living glossary, NSE-012 codebooks).

## NSE-017 — Domain-specific / repo-specific / author-org codec considerations

The codec must be conditioned on the deployment context, not trained globally:

- **Repo-specific:** a codec trained on one repository's module ontology, identifier conventions, repeated phrases, and AST patterns (e.g., a Python study scoped to a single repo) will outperform a generic cross-repo dictionary on that repo. `zipf_fork` verifies power-law behavior in programming-language token usage on the Flask codebase across 885 Python files / ~19,541 keywords — a direct template for repo-scoped conditional-frequency codec training.
- **Author / org-specific:** personal recurring vocabulary, naming conventions, role, and intended social register shape candidate forms (NSE-012 author/speaker-profile codebook). Org-level dialects (shared group acronyms, project shorthand) are a separate codebook scope.
- **Domain-specific:** finance, science, engineering, sales, planning, etc. carry high-frequency specialized vocabulary (NAV, IRR, PCR, CAD, CI/CD, AST, RAG) that warrants its own codebook.
- **Language-stack-specific:** the natural-language of the repo (English, Japanese, Russian, …) plus the programming languages in use interact with the chosen LLM tokenizer — measure both.

Reference study corpora (forked + starred as "Agentic Language Development Research" / "Domain Specific Codecs/Dialects" / "Concept Adaptation referenceTemplate"):

- [zipfs-law_fork](https://github.com/timerloggedout-spec/zipfs-law_fork) — Zipf's law in natural language; word-frequency analyzer, CSV export, histograms (frequency-vs-rank baseline).
- [zipf_fork](https://github.com/timerloggedout-spec/zipf_fork) — Zipf's law for programming languages; repo-scoped Python study on Flask (885 files / ~19,541 keywords); reports only the first few keywords follow a distribution — informs how far power-law abbreviation holds for code tokens.
- [twitter_sentiment_analysis_part3_fork](https://github.com/timerloggedout-spec/twitter_sentiment_analysis_part3_fork) — Zipf's law + text visualization; custom positivity metric (Bokeh); sentiment as a domain codec test corpus.
- [hypemergence_fork](https://github.com/timerloggedout-spec/hypemergence_fork) — predicting emerging artists via SVM classification on normalized multi-source social time-series (Echonest, SoundCloud, YouTube, Facebook, Twitter, Last.fm, Instagram); emergence/complexity reference + multi-source feature-compression template.

## NSE-018 — Falsifiable research question & control conditions

Primary RQ: *Does constrained, tokenizer-aware span-level multilingual rendering reduce total task cost while retaining or improving task quality vs the best monolingual prompt?*

Controls: (1) English-only canonical; (2) each language alone, professionally translated; (3) best single-language oracle (lowest-token monolingual); (4) translate-to-min-token language; (5) random-switch control (same switch count, random locations — if it matches ADLM, the gain is a tokenizer artifact, not semantic compression); (6) natural bilingual code-switch; (7) symbol-only/glossary-only; (8) ADLM policy. Tokenizer-specific and model-specific policy: token counts may transfer, comprehension behavior often will not.

## Acceptance criteria

- #320, #309, #182, and #175 are explicitly connected in the proposal registry/source; related issues expanded to include #126, #304, #196, #177, #208, #274 (per #309/#182 maps).
- Canonical notation is separated from aliases and domain-specific syntax.
- Human density, tokenizer efficiency, and LLM concept-delivery efficiency are reported as distinct layers.
- The glossary/index design has provenance, lifecycle, and codebook-scope semantics; codebooks are layered and context-conditioned (universal / model-tokenizer / language-script / domain / repo / team / author / session).
- Agent communication uses the compressed form as medium with a canonical-IR truth layer; external info is transmuted + compressed into indexes/libraries/dictionaries on ingest.
- Codec conditioning is repo-/author-/org-/domain-/language-stack-specific; the forked Zipf corpora are the reference study set for conditional-frequency training.
- Compression preserves semantic category, directionality, composition order, identity, and domain scope (NSE-002 contract).
- Existing repository indexes are integration targets, not discarded.
- The proposal remains malleable by design (NSE-004 loop, NSE-008 ledger) — it is intended to be continuously modified as research and implementation evolve.
- Execution work remains gated by proposal acceptance and `repo-gate` + `termux-smoke`.
