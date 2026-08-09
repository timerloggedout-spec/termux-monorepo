# Bolt's Performance Journal

Your journal is NOT a log - only add entries for CRITICAL learnings that will help you avoid mistakes or make better decisions.

## 2026-08-01 - SQLite Insert Loops and Stale Closed Connections in Multi-Agent Indexing
**Learning:**
In the multi-agent's project file indexing system, SQLite connections were being opened and closed per project file, and database inserts (nodes and edges) were performed individually inside nested loops (`cursor.execute`). Even worse, in some source versions of `src/db.py`, the connection block exits before doing the edge inserts, causing silent failures on a closed database connection that went unnoticed due to `except Exception: pass`.
Using a single shared database connection across file walks and batching all inserts with `cursor.executemany` yields a massive performance boost (saving connection/transaction disk I/O) and guarantees transactional integrity.

**Action:**
Always batch SQL database operations using `executemany` instead of iterating with `execute`. Provide support for passing an optional shared `conn` handle in indexing/utility functions to allow single-connection batch runs across walk loops, while safely closing connections only if opened locally.

## 2026-08-02 - Incremental I/O and State Tracking for Real-Time Log Telemetry Parsing
**Learning:**
The Termux multi-agent orchestration dashboard repeatedly scans and parses the entire `agent_telemetry_stream.json` file from the start every second. On long-running refactoring or multi-agent pipelines, the log file grows, transforming the telemetry read operation into a major CPU and I/O bottleneck (O(N) complexity). By implementing state-tracking globals (`_last_file_pos` and `_active_jobs_cache`) and utilizing `seek/tell` operations, the parser only scans newly appended lines, reducing parsing complexity to O(1) for subsequent reads and yielding a >100x speedup. It is also critical to handle the edge case where the log file is truncated, deleted, or recreated, by comparing `file_size < _last_file_pos` and resetting the tracking state dynamically.

**Action:**
For all real-time stream parsers, event loops, or active polling operations, use stateful incremental I/O (seek/tell tracking and in-memory caches) instead of full-file rescans. Always build in a self-healing reset trigger for truncation or deletion of the underlying log stream.
