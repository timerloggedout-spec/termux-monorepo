# Legacy Local Snapshot Pipeline — Gap Audit

<badge color="danger">Disconnected / requires repair</badge>

**Observed:** archwiz/trace_data_flow.py scans local source directories for data-file path strings and writes $HOME/tmp/data_flow_map.txt. archwiz/build_data_flow_manifest.py reads $HOME/central_index.jsonl and the temporary map, then writes to absolute path $HOME/archwiz/DATA_FLOW_MANIFEST.md. The builder stamps a wall-clock Generated field and indexed-file count. The tracked archwiz/DATA_FLOW_MANIFEST.md blob is zero bytes at observed master SHA 5135731c389c6b1b8ed8332b3415a60f8163c2a1.

**Findings:** output path mismatch; no source SHA/tree SHA/generator version/input digest; substring/basename heuristics create candidate matches, not verified writer edges; temporary map is untracked scratch; central_index.jsonl lacks repo-owned freshness/coverage contract; no verified consumer reaches CRG/SHE/EPS; Generated proves run time, not input freshness.

**Repair contract:** resolve repo root from script location or explicit output path; publish to declared repo-owned generated directory; include generated_at, source_sha, tree_sha, generator_version, input_manifest_sha256, indexed_file_count, mapped_file_count, coverage_status and unmapped_count; classify heuristic matches as candidate; add freshness validation. Connect to CRG/SHE only after provenance and coverage pass.

Actual local generated_at remains unknown; this audit does not infer it.
