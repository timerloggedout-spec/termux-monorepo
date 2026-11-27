# Source and current-state evidence

## Canonical sources

- `archwiz/trace_data_flow.py`: legacy scanner; reads `~/tmp/data_files_list.txt`, scans hard-coded home directories, writes `~/tmp/data_flow_map.txt`.
- `archwiz/trace_data_flow_safe.py`: safer scanner variant with symlink exclusion, hidden-directory pruning, and a 500 KB file cap; it retains the same fixed input/output paths.
- `archwiz/build_data_flow_manifest.py`: reads `~/central_index.jsonl` and `~/tmp/data_flow_map.txt`; writes `~/archwiz/DATA_FLOW_MANIFEST.md`; records wall-clock time and indexed count; uses a faulty basename fallback for writer mapping.
- `archwiz/aether.py`: exposes `manifest` and `reindex manifest` commands.
- `archwiz/reindex_pipeline.py`: exposes the same builder through the legacy reindex pipeline.
- `archwiz/DATA_FLOW_MANIFEST.md`: tracked file observed as empty at the architecture audit baseline.

## Verified consumers

- `archwiz/aether.py` reads the manifest for duplicate reporting and invokes the builder for `manifest` / `reindex manifest`.
- `archwiz/reindex_pipeline.py` invokes the builder during the manifest stage.
- `archwiz/build_reference_hub.py` reports the manifest's path and size.

## Current evidence gaps

- The repository does not contain the local `central_index.jsonl` or `data_files_list.txt` inputs.
- GitHub CI cannot recreate the device-local snapshot from repository files alone.
- Existing lexical path mentions establish candidate references, not proven write operations.
- A wall-clock timestamp alone does not identify the source tree or the inputs used.

## Privacy boundary

Keep local indexes, data-file lists, browser/session stores, and temporary flow maps outside Git. Commit only generator code, tests, compact documentation, and an explicitly ungenerated status marker until a local run can provide real inputs.
