# NSE-021 — Sidecar Comment Overlays and Siglary DoE Tournament

**Status:** accepted design — Operator vote recorded 2026-11-21 (term `NSE-021/1`)  
**Implements:** NSE-021  
**Parent proposal:** `notation-sets-evolution`  
**Related:** NSE-005 (context-relationship integration), NSE-007 (drift detection), NSE-008 (evolution ledger), ICM-03 (documentation-only maintenance pipeline), ICM-07 (master-rebuild integration evidence), `docs/ops/DOE-FAMILY.md`

## Intent

Run a controlled, reversible comparison of English, registered Siglary operators, dense notation, and hybrid rendering across ICM documentation, LLM-map documentation, and code comments. Keep canonical source files byte-identical during experimentation. Store every treatment as a sidecar overlay and materialize disposable variants for DoE/MVT evaluation.

The release path promotes only a validated winning overlay into a comment-only or documentation-only patch. Executable code tokens, API contracts, identifiers, literals, links, commands, paths, and quoted evidence retain their original bytes and meaning.

## Goals

1. Establish a canonical, content-addressed overlay format for Markdown prose and syntax-aware code comments.
2. Support file-, section-, and comment-level treatment mixing under one source SHA.
3. Preserve the README-declared root roles: `CLAUDE.md` is the primary collaborator entry and `CLAUDE.hum.md` is the Linguist/tooling-compatibility surface. Record the historical `AGENTS.md` ↔ `AGENTS.hum.md` projection lineage and blob-identical rename into `CLAUDE.hum.md` without inferring a current 1:1 root projection.
4. Compare treatment variants through the existing DoE family and MVT/ATES separation.
5. Promote notation through small, reviewable releases with deterministic semantic and syntax integrity checks.

## Non-goals

- Rewrite executable code, identifiers, docstrings, string literals, directives, or runtime behavior.
- Convert generated indexes or reports as canonical inputs.
- Replace the existing DoE record schema, provider attribution, ICM maintenance workflow, or proposal lifecycle.
- Treat token reduction as a quality proxy or a single composite score as the promotion authority.
- Merge the stale ICM adaptation branch as an integration base.

## Approaches

| Approach | Benefit | Trade-off |
|---|---|---|
| Git branches/worktrees per treatment | Native Git diffs and independent CI | Whole-file branch variants make fine-grained mixing and treatment attribution expensive |
| Git notes | Lightweight provenance attached to commits | Notes do not materialize as working-tree content and require explicit ref transport |
| **Content-addressed sidecar overlays** | Fine-grained mixing, shared source SHA, reversible rendering, and independent treatment digests | Requires stable anchors, an overlay validator, and a materializer |

**Selected:** content-addressed sidecar overlays. Use Git branches/worktrees only to materialize and validate an assigned treatment. Git's object database shares unchanged source blobs across worktrees and branches.

## Canonical model

Each campaign pins a source snapshot and records overlays separately:

```text
campaign/
  DESIGN.json
  MANIFEST.json
  tasks/
  overlays/{control-en,operators-v1,dense-v1,hybrid-v1}/
  assignments/
  records/
  analysis/
  releases/
```

Each overlay entry carries:

- `overlay_schema_version`, `campaign_id`, `variant_id`, `notation_version`, `renderer_version`;
- `source_path`, source Git blob SHA, source SHA-256, parser/language version;
- stable `anchor_id`, anchor kind, AST node kind, owner symbol or Markdown heading path, context fingerprint, duplicate ordinal;
- canonical semantic IR reference and replacement surface text;
- provenance, creation timestamp, and validation status.

Use a stable anchor derived from path + language + owner symbol + syntax-node type + neighboring non-comment token fingerprint + local ordinal. Use Markdown heading path + block type + block ordinal + source fingerprint. Line and column values remain diagnostics; they do not define identity. Treat changed source hashes as stale-overlay events that require re-anchoring and validation.

## Corpus and mapping inventory

Initial Markdown census: 78 paths under `docs/icm/` and 13 under `workspace/llm_map/` (91 raw candidates). Classify each as canonical/live, generated, historical/sealed, captured, stale, or excluded before conversion. Derive code-comment candidates from authoritative ICM cards and LLM-map source references, then enumerate syntax-aware comment nodes by language.

Maintain a mapping ledger for every relevant `CLAUDE.md`, `CLAUDE.hum.md`, `AGENTS.md`, and `AGENTS.hum.md` path and declared relationship:

- canonical source path and related projection/compatibility path;
- historical aliases and rename/migration commits;
- source/projection blob SHA and semantic mapping version;
- CedrLang/renderer version and round-trip fixture ID;
- relationship kind: direct projection, compatibility alias, historical rename, or independent entry;
- explicit status: aligned, drifted, pending migration, or exempt with rationale.

Historical evidence to preserve: PR #196 / commit `ea2a2f8` (CedrLang v2 round-trip); commits `501ae93`, `9aeb0f3`, and `bcebb57` (human projection synchronization); commit `01c8dc9` (blob-identical `AGENTS.hum.md` → `CLAUDE.hum.md` rename and inbound-reference sweep). Treat the root `CLAUDE.hum.md` as a Linguist/tooling-compatibility surface per README. Compare it with root `CLAUDE.md` only under an explicitly approved mapping; preserve its historical `AGENTS.hum.md` lineage.

The mapping test enumerates every declared projection, compatibility alias, historical rename, and independent entry; verifies each path exists or has a recorded migration disposition; validates inbound links; and checks exact round-trip behavior only for pairs with an explicit round-trip contract. A renamed path retains its prior aliases and commit provenance.

## Transformation boundaries

### Markdown

Parse Markdown into an AST. Transform eligible prose nodes only. Preserve front matter, headings, tables, code fences, inline code, URLs, file paths, commands, flags, identifiers, numeric literals, quotations, citations, and generated/historical sealed content. Record each transformed block as a separate overlay entry.

### Code comments

Use Tree-sitter parsers for each language in the bounded source inventory. Select comment nodes only. Preserve docstrings/string literals, annotations, preprocessor directives, compiler attributes, shebangs, pragmas, suppression directives, and executable tokens. Start with standalone comments and line comments; treat documentation comments as a separately measured cohort after fixtures establish parser coverage.

### Semantic representation

Normalize each eligible span into a canonical semantic IR with fixed fields: scope, actor/owner, action, constraint, expected state, evidence, and exceptions. Render four treatments: English control, operator-first, dense registered notation, and hybrid. Resolve each operator through the canonical Siglary registry. Keep OPERATORS, GLYPHS, and CHORDS as distinct typed classes. Attach a human-readable expansion for ambiguous or low-confidence spans.

## Integrity gates

1. **Source immutability:** source blob SHA remains identical throughout the experiment.
2. **Executable-token invariant:** normalized non-comment code token stream hashes match before and after materialization.
3. **Parser integrity:** every materialized code file parses successfully in its original language mode.
4. **Markdown integrity:** AST structure, protected spans, links, headings, and code fences remain valid.
5. **Semantic round-trip:** decode(render(IR)) equals the canonical IR; preserve exact source text for protected spans.
6. **Mapping integrity:** declared CLAUDE/AGENTS relationships and historical aliases pass mapping fixtures.
7. **Human comprehension:** blinded reviewers correctly recover scope, action, constraints, expected state, and evidence.
8. **Provenance:** every overlay and run links to source SHA, variant, renderer, notation set, task, configured model instance, prompt/tool hashes, and timestamp.

## DoE / MVT design

Use the existing DoE family and `EXPERIMENT.schema.json` as the record contract. Keep campaign-specific treatment assignment and overlay digests in a companion manifest keyed by run ID; evolve the shared schema only through its own accepted scope. Keep the campaign design-only until committed run evidence satisfies the DoE family admission contract. Keep code-reference MVT/ATES comparisons separate from model/provider task dispatch; record each execution lane with its own configured-instance provenance.

Factors:
- representation: English / operators / dense / hybrid;
- context placement: entry point / related context / mixed;
- surface: ICM Markdown / LLM-map Markdown / code comments.

The full factorial is 4 × 3 × 3 = 36 cells. Use staged screening before full interaction testing:

1. Screen the four representations on a fixed, stratified task set.
2. Run MVT on context placement and surface.
3. Expand to the factorial interaction design for surviving treatments.
4. Repeat promising arms on held-out tasks and additional configured model instances.
5. Freeze the winning renderer and notation version for a release candidate; run backfill as a separately identified provenance class.

Randomize or block treatment order. Keep source SHA, task identity, context set, model@version, configured instance key, prompt/tool hashes, and repetitions fixed or explicitly stratified. Record all runs, including failures, skips, censored observations, and manual interventions.

Primary outcomes: task correctness, semantic preservation, comprehension, evidence/citation accuracy, integration correctness, and parse/contract validity. Secondary outcomes: input/output/repair tokens, latency, rework cycles, ambiguity, cross-model portability, and human intervention.

Apply a quality-first gate: require the pre-registered quality and validity floors, then compare tokens, latency, and cost on a Pareto frontier. Preserve raw metrics and per-arm distributions. Treat latency and token reduction as secondary to correctness.

## Release and version identity

Version source, notation, renderer, and experiment design independently. Identify each treatment by:

`variant_id = H(source_sha256 || notation_version || renderer_version || design_sha256 || overlay_digest)`

A notation release creates a new immutable overlay version and a focused patch generated from the selected overlay. Preserve the canonical source and all prior overlay versions. Re-score historical observations under changed scoring definitions with explicit live/backfill provenance.

## Acceptance criteria for NSE-021

- Complete bounded inventory and classification for ICM/LLM Markdown candidates.
- Complete historical mapping ledger for CLAUDE/AGENTS human projections and rename aliases.
- Overlay schema, validator, materializer, and stable-anchor extractor with fixtures.
- Tests prove source immutability, executable-token invariance, parse validity, Markdown protection, mapping round-trip, and stale-anchor handling.
- Pre-registered staged DoE design and task assignment protocol.
- At least one replicated, held-out comparison with quality floors met before any notation promotion.
- PRs cite `Implements: NSE-021`; required repo gates pass on the exact head SHA.

## Governance and dependencies

Use ICM-03's completed documentation-only maintenance pipeline as the repository-native ICM process reference, including its inventory, design, verification, promotion, and human-review boundaries. The ICM `-r2` branch remains historical comparison evidence; base new integration work on current `master` and the completed ICM-03/ICM-07 repository-native maintenance artifacts. The Operator accepted NSE-021 on 2026-11-21 (term `NSE-021/1`). The parent notation proposal retains its broader `posted` state. Execute parser, materializer, and corpus conversion work within the accepted NSE-021 item. Use the existing proposal, DoE, MVT, and dual-gate lifecycle.
