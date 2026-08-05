# Bolt's Performance Journal

Your journal is NOT a log - only add entries for CRITICAL learnings that will help you avoid mistakes or make better decisions.

## 2026-08-01 - SQLite Insert Loops and Stale Closed Connections in Multi-Agent Indexing
**Learning:**
In the multi-agent's project file indexing system, SQLite connections were being opened and closed per project file, and database inserts (nodes and edges) were performed individually inside nested loops (`cursor.execute`). Even worse, in some source versions of `src/db.py`, the connection block exits before doing the edge inserts, causing silent failures on a closed database connection that went unnoticed due to `except Exception: pass`.
Using a single shared database connection across file walks and batching all inserts with `cursor.executemany` yields a massive performance boost (saving connection/transaction disk I/O) and guarantees transactional integrity.

**Action:**
Always batch SQL database operations using `executemany` instead of iterating with `execute`. Provide support for passing an optional shared `conn` handle in indexing/utility functions to allow single-connection batch runs across walk loops, while safely closing connections only if opened locally.

## 2026-08-05 - File Seek Position Tracking and Graceful Optional Imports in Terminal Dashboards
**Learning:**
In terminal-based live-monitoring applications, continuously polling growing append-only JSON log files to update UI dashboards causes severe CPU and I/O degradation. Tracking file seek positions (`f.tell()`) and keeping an in-memory accumulated dictionary of updates transforms the polling operation from $O(N)$ (where $N$ is total lines in log) to $O(M)$ (where $M$ is newly appended lines), resulting in a >170x performance gain. Additionally, avoiding `sys.exit(1)` at import time for optional CLI dependencies (like `rich`) and handling them lazily at script execution prevents import crashes in automated test environments.

**Action:**
Use stateful file-pointer seek offsets and in-memory caches to incrementally process append-only logs instead of re-reading from scratch. Ensure optional third-party library dependencies (such as `rich`) only fail during script execution, never at import time.
