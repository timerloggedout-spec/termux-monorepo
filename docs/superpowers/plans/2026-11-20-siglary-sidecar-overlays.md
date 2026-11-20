# Plan — NSE-021 Sidecar Comment Overlays

**Implements:** NSE-021  
**Design:** [Siglary Sidecar Overlays design](../specs/2026-11-20-siglary-sidecar-overlays-design.md)  
**Execution state:** plan only; implementation starts after proposal acceptance.

## Task 1 — Register the scope and preserve lineage

**Files**
- `docs/proposals/active/notation-sets/ITEMS.md`
- `docs/proposals/active/notation-sets/MANIFEST.md`
- `docs/proposals/active/notation-sets/NSE-021-SIDECAR-OVERLAYS.md`

**Work**
- Add NSE-021 with the bounded ICM/LLM Markdown and syntax-aware code-comment scope.
- Link NSE-020, ICM-08, DoE family, and MVT/ATES separation.
- Record historical migration commits and the current CLAUDE projection drift as an inventory finding.

**Verification**
- Run proposal registry validation and item/manifest consistency checks.
- Confirm existing proposal status remains `posted` pending Operator acceptance.

## Task 2 — Build the inventory and mapping ledger

**Files**
- `experiments/doe/siglary-context-tournament/inventory/`
- `tests/fixtures/linguist_projection/`

**Work**
- Enumerate all `docs/icm/**/*.md` and `workspace/llm_map/**/*.md` paths.
- Classify canonical, generated, historical/sealed, captured, stale, and excluded content.
- Trace all current and historical `CLAUDE.md`, `CLAUDE.hum.md`, `AGENTS.md`, and `AGENTS.hum.md` paths through Git history.
- Record aliases, rename commits, source/projection hashes, renderer version, and fixture IDs.
- Discover code-comment files through authoritative ICM/LLM source references, then inventory parser-supported comment nodes.

**Tests**
- Inventory completeness against Git tree paths.
- Mapping alias coverage and inbound-link checks.
- Historical fixture reproduction for #196 and the rename commit.

## Task 3 — Implement the sidecar contract

**Files**
- `experiments/doe/siglary-context-tournament/schema/overlay.schema.json`
- `scripts/notation/overlay_validate.py`
- `tests/test_siglary_overlay_schema.py`

**Work**
- Define versioned overlay records with source SHA, stable anchor, semantic IR, replacement text, notation/renderer versions, and provenance.
- Validate schema, source freshness, unique anchor identity, and protected-span boundaries.
- Treat stale source hashes as explicit re-anchoring events.

**TDD**
- Add failing schema and stale-source tests first.
- Implement the minimal validator.
- Run focused tests and repository documentation/CI checks.

## Task 4 — Implement stable anchors and syntax-aware extraction

**Files**
- `scripts/notation/overlay_extract.py`
- `tests/test_siglary_overlay_anchors.py`
- `tests/fixtures/siglary_overlay/`

**Work**
- Extract Markdown AST prose blocks and Tree-sitter comment nodes.
- Build stable IDs from source path, owner/syntax context, token fingerprints, and ordinals.
- Keep line/column data as diagnostics.
- Preserve docstrings, directives, pragmas, strings, identifiers, and executable syntax.

**Tests**
- Stable ID across line-only movement.
- Changed neighboring token triggers stale-anchor review.
- Comment extraction leaves all non-comment tokens unchanged.
- Markdown extraction preserves protected nodes.

## Task 5 — Implement renderer and disposable materializer

**Files**
- `scripts/notation/overlay_render.py`
- `scripts/notation/overlay_materialize.py`
- `tests/test_siglary_overlay_materialize.py`

**Work**
- Normalize spans to canonical semantic IR.
- Render English, operator-first, dense, and hybrid treatments from the same IR.
- Resolve symbols through the registered Siglary taxonomy.
- Materialize assigned variants in disposable worktrees or temporary trees.
- Emit a manifest linking materialized paths to source SHA and overlay digest.

**Tests**
- Semantic encode/decode round-trip.
- Protected span byte equality.
- Source tree SHA invariance.
- Executable-token stream hash equality.
- Parse validity for every supported language fixture.

## Task 6 — Pre-register and execute staged DoE/MVT

**Files**
- `experiments/doe/siglary-context-tournament/DESIGN.json`
- `experiments/doe/siglary-context-tournament/MANIFEST.json`
- `experiments/doe/siglary-context-tournament/tasks/`
- `experiments/doe/siglary-context-tournament/assignments/`
- `experiments/doe/siglary-context-tournament/records/`

**Work**
- Reuse the existing DoE family record contract.
- Key companion treatment records by run ID and include overlay/source/context hashes.
- Stratify task difficulty and surface; randomize treatment order.
- Run representation screening, MVT placement/surface comparison, factorial interaction testing, then held-out replication.
- Preserve failed, skipped, censored, and manually intervened runs.

**Verification**
- Validate every run record against the current experiment schema.
- Verify source/task/configured-instance identity for every comparison.
- Confirm primary quality floors before resource-efficiency ranking.

## Task 7 — Analyze, review, and release

**Files**
- `experiments/doe/siglary-context-tournament/analysis/`
- `experiments/doe/siglary-context-tournament/releases/`
- generated comment/documentation-only patch

**Work**
- Report raw outcomes, confidence intervals, quality gates, and Pareto frontier.
- Select a treatment only when held-out replication confirms quality.
- Generate a small comment/documentation-only patch from the winning overlay.
- Keep every prior overlay immutable and versioned.
- Update notation evolution records and ICM references through their owning proposal scope.

**Verification**
- Independent review of semantic diffs and source invariants.
- Run `python3 scripts/ci/repo_gate.py` and `python3 scripts/ci/termux_smoke.py`.
- Re-fetch the PR head SHA and inspect exact-head jobs, steps, logs, and artifacts before promotion.
