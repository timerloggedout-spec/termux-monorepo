# ArchWiz Data-Flow Manifest Provenance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Repair the ArchWiz data-flow snapshot pipeline with configurable paths, provenance metadata, honest coverage, candidate-only mention semantics, and reliable failure propagation.

**Architecture:** Keep the current JSONL index and text flow-map formats. Add a safe scanner CLI and a checkout-relative manifest builder, preserve Termux defaults, and route the legacy scanner entry point through the safe implementation. Downstream Aether/reindex callers propagate the builder's exit status.

**Tech Stack:** Python 3.9+ standard library, Git CLI for source identity, pytest fixtures.

**Spec:** `docs/superpowers/specs/2026-11-21-archwiz-data-flow-manifest-design.md`

## Global Constraints

- Python standard library only.
- Preserve default local inputs: `~/central_index.jsonl`, `~/tmp/data_flow_map.txt`, `~/tmp/data_files_list.txt`.
- Default manifest output: `archwiz/DATA_FLOW_MANIFEST.md` relative to the builder file.
- Keep device-local data lists, indexes, and flow maps outside Git.
- Record UTC `generated_at`, source SHA, tree SHA, generator version, input digests, coverage, and indexed/mapped/unmapped counts.
- Treat lexical matches as candidate mentions, never verified writer edges.
- Preserve the existing Aether command surface and return generator failures to the caller.

## Review Focus

- Missing index: return non-zero and preserve the previous manifest.
- Missing or malformed flow map: report partial coverage and zero/known mapped counts.
- Invalid JSONL rows and duplicate paths: count invalid rows and produce deterministic path ordering.
- Git metadata unavailable: record `unknown` and `UNVERIFIED` coverage.
- Paths containing spaces, symlinked directories, hidden directories, and oversized source files: retain safe scanning behavior.

---

### Task 1: Lock down the snapshot contract with tests

**Files:**
- Create: `tests/test_archwiz_data_flow_manifest.py`
- Modify: `tests/test_aether_reindex.py`

**Interfaces:**
- Builder CLI: `--index`, `--flow-map`, `--output`, `--repo-root`; callable `main(argv=None) -> int`.
- Scanner CLI: `--data-files`, repeatable `--source-dir`, `--output`, `--max-file-bytes`; callable `main(argv=None) -> int`.

- [ ] Write tests for builder metadata/hash/coverage, candidate-only labels, missing-index preservation, malformed rows, and explicit output paths.
- [ ] Write scanner tests for explicit inputs, symlink exclusion, hidden/cache pruning, and maximum file size.
- [ ] Add Aether tests proving `cmd_manifest` propagates a failed subprocess status.
- [ ] Run the focused tests and verify expected failures before production edits.

### Task 2: Implement the manifest builder

**Files:**
- Modify: `archwiz/build_data_flow_manifest.py`

**Interfaces:**
- `load_central_index(path) -> (records, invalid_count)`
- `load_flow_map(path) -> mapping`
- `build_manifest(records, flow_map, metadata) -> str`
- `main(argv=None) -> int`

- [ ] Add CLI parsing and checkout-relative default output.
- [ ] Hash the exact index and flow-map bytes.
- [ ] Read source SHA/tree SHA from Git and emit `unknown` when unavailable.
- [ ] Emit UTC timestamp, generator version, counts, and coverage.
- [ ] Remove the invalid basename fallback; label exact text matches as candidate mentions.
- [ ] Write output atomically and preserve existing output when required inputs are missing.
- [ ] Run focused builder tests.

### Task 3: Unify scanning and propagate status

**Files:**
- Modify: `archwiz/trace_data_flow_safe.py`
- Modify: `archwiz/trace_data_flow.py`
- Modify: `archwiz/aether.py`
- Modify: `archwiz/reindex_pipeline.py`

**Interfaces:**
- Scanner `main(argv=None) -> int` writes the existing text flow-map format.
- Legacy scanner delegates to the safe scanner.
- Aether `manifest` returns the subprocess exit status.
- Reindex pipeline invokes Python via an argument-safe command and preserves the exit code.

- [ ] Implement explicit scanner input/source/output arguments while preserving Termux defaults.
- [ ] Keep symlink, hidden-directory, cache, and size guards.
- [ ] Delegate the legacy scanner entry point to the safe implementation.
- [ ] Propagate failures through Aether and reindex pipeline callers.
- [ ] Run scanner and caller tests.

### Task 4: Document and validate the repaired workflow

**Files:**
- Modify: `archwiz/DATA_FLOW_MANIFEST.md`
- Modify: `archwiz/TOOL_INDEX.md`
- Modify: `docs/icm/objects/operations/archwiz.md`
- Modify: `docs/architecture/flows/legacy-snapshot-audit.md`
- Modify: `docs/architecture/flows/legacy-snapshot-audit.mmd`

**Interfaces:**
- Documentation lists exact default and override CLI paths.
- The tracked manifest marks the runtime snapshot as `UNGENERATED` until real local inputs exist.

- [ ] Add a concise ungenerated marker without fabricating local counts or timestamps.
- [ ] Document scanner, builder, and Aether entry points.
- [ ] Update the ICM route and historical gap map with the repaired code contract and remaining device-only validation.
- [ ] Run focused tests, documentation/link validation, `python3 scripts/ci/repo_gate.py`, and `python3 scripts/ci/termux_smoke.py`.
- [ ] Record current SHA and required GitHub checks in the proposal.

## Commit sequence

1. `docs(archwiz): register snapshot provenance repair`
2. `test(archwiz): specify data-flow snapshot contract`
3. `fix(archwiz): add provenance to data-flow snapshots`
4. `fix(archwiz): propagate snapshot generator failures`
5. `docs(archwiz): document snapshot provenance workflow`

Every commit includes `Implements: ARCH-SNAPSHOT-001`.
