# 4_51GH7 Research Audit — Existing Data Sources

Generated: 2026-06-06T21:36:01.253242+00:00

## run_history.jsonl
- Total entries: 6
- Unique files: 6
- Files with PASS: 6
- Files with FAIL: 0

## termux-multi-agent/local_repo.db
- Tables: ['nodes', 'edges', 'run_history', 'sqlite_sequence', 'sessions', 'messages', 'messages_fts', 'messages_fts_data', 'messages_fts_idx', 'messages_fts_docsize', 'messages_fts_config']
  - nodes: 0 rows
  - edges: 0 rows
  - run_history: 16 rows
  - sqlite_sequence: 1 rows
  - sessions: 16 rows
  - messages: 1500 rows
  - messages_fts: 1500 rows
  - messages_fts_data: 45 rows
  - messages_fts_idx: 43 rows
  - messages_fts_docsize: 1500 rows
  - messages_fts_config: 1 rows

## Telemetry Files
- Count: 1
  - agent_telemetry_stream.json (975 bytes)

## temporal_provenance.json
- Type: dict
- Keys: 452
  - cli-synthegration/codex/blobs/05054373f9c5ce71.blob: ['session', 'node_id', 'block_idx', 'timestamp_utc', 'hash', 'snippet', 'delay_seconds']
  - cli-synthegration/codex/blobs/6e3542c7bebfd9ed.blob: ['session', 'node_id', 'block_idx', 'timestamp_utc', 'hash', 'snippet', 'delay_seconds']
  - cli-synthegration/codex/blobs/e340e593b7e2d737.blob: ['session', 'node_id', 'block_idx', 'timestamp_utc', 'hash', 'snippet', 'delay_seconds']
  - cli-synthegration/codex/blobs/21a2b8487d188ca1.blob: ['session', 'node_id', 'block_idx', 'timestamp_utc', 'hash', 'snippet', 'delay_seconds']
  - cli-synthegration/codex/blobs/5f89d5c8f883d28a.blob: ['session', 'node_id', 'block_idx', 'timestamp_utc', 'hash', 'snippet', 'delay_seconds']

## true_versions.json
- Type: dict
- Entries: 103
  - deepcli/add-parent-id.patch.py: [{'session': 'ea90d423-8ebb-456f-a44f-8c85464fa722', 'node_id': '64', 'block_idx': 3, 'timestamp_utc
  - deepcli/add-history-ids.patch.py: [{'session': 'ea90d423-8ebb-456f-a44f-8c85464fa722', 'node_id': '64', 'block_idx': 0, 'timestamp_utc
  - deepcli/extract-token.js: [{'session': 'ea90d423-8ebb-456f-a44f-8c85464fa722', 'node_id': '36', 'block_idx': 0, 'timestamp_utc

## correlation_index.json
- Type: dict
- Keys: 2
  - meta
  - correlations

## llm_index_compact.jsonl
- Fields present: ['p', 'pj', 'l', 'b', 'ts', 's', 't', 'h', 'as', 'by', 'ah']
- ts: 1776/1776 populated
- ah: 0/1776 populated
- by: 1684/1776 populated
- as: 246/1776 populated
- fr: FIELD MISSING
- vr: FIELD MISSING

## Scripts that write verdict-like data
