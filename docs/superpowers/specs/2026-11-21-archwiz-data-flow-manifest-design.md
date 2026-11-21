# ArchWiz Data-Flow Manifest Provenance — Design

## Intent

Make the legacy ArchWiz snapshot pipeline reproducible across Termux and CI while retaining its current local input formats. The manifest becomes an auditable snapshot: source identity, input identity, generation time, coverage, and confidence labels travel together.

## Goals

- Resolve the output from the generator's checkout location by default.
- Accept explicit index, flow-map, source-root, data-list, and output paths.
- Preserve the existing local defaults for Termux use.
- Record `generated_at` (UTC), `source_sha`, `tree_sha`, `generator_version`, `input_manifest_sha256`, `flow_map_sha256`, `indexed_file_count`, `mapped_file_count`, `coverage_status`, and `unmapped_count`.
- Label string/path matches as candidate mentions; retain `unknown` when evidence is absent.
- Preserve atomic output and propagate command failures.
- Keep all device-local inputs outside Git.

## Non-goals

- Claiming actual write semantics from lexical matches.
- Building an AST/dataflow analyzer.
- Uploading local indexes or device state to GitHub.
- Regenerating the local manifest without its real input files.
- Refactoring unrelated ArchWiz tools or the reference-hub pipeline.

## Approaches

1. **Compatibility-first CLI and provenance (chosen).** Keep the JSONL and text flow-map formats, add explicit path arguments, derive the default output from the script's checkout path, add provenance/coverage metadata, and classify matches as candidates. This minimizes migration risk and supports fixtures in CI.
2. **Replace lexical scanning with AST writer analysis.** This could improve semantic precision but expands language support, parser dependencies, and false-negative risk. It does not solve missing input provenance or output-path portability by itself.
3. **Documentation-only repair.** This is low risk but leaves the hard-coded paths, fragile mapping fallback, and weak failure propagation in place.

The compatibility-first approach is selected because the current pipeline already has consumers and known input formats. It repairs the provenance and portability boundary without inventing a new data model or claiming stronger semantics.

## Design decisions

- Python standard library only.
- The builder's default output is `archwiz/DATA_FLOW_MANIFEST.md` relative to `__file__`.
- Default local inputs remain `~/central_index.jsonl`, `~/tmp/data_flow_map.txt`, and `~/tmp/data_files_list.txt`.
- CLI arguments override every input/output path; repeated `--source-dir` values override the legacy source-root list.
- Missing required index input returns a non-zero status and preserves any existing output.
- Missing flow-map input yields `PARTIAL` coverage with zero mapped records; malformed index rows also reduce coverage.
- Source and tree identities come from `git -C <repo-root> rev-parse`; unavailable Git metadata is recorded as `unknown` and yields `UNVERIFIED`.
- All lexical matches are displayed as `candidate mention`, never as a verified writer.
- The legacy `trace_data_flow.py` entry point delegates to the safer CLI implementation.
- Output is written atomically after successful validation.

## Acceptance

The focused tests prove explicit path handling, missing-input behavior, hash metadata, source/tree SHA, coverage accounting, candidate labeling, symlink exclusion, bounded file reads, and non-zero failure propagation through Aether/reindex callers. Repository CI runs the fixtures without requiring device-local data.

## Runtime boundary

The local Termux regeneration remains a separate verification step because the source index and data-file list are device-local and are absent from the repository. The tracked file remains an explicit `UNGENERATED` marker until that run occurs.
