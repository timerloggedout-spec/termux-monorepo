# Bolt's Performance Journal

Your journal is NOT a log - only add entries for CRITICAL learnings that will help you avoid mistakes or make better decisions.

## 2026-08-01 - SQLite Insert Loops and Stale Closed Connections in Multi-Agent Indexing
**Learning:**
In the multi-agent's project file indexing system, SQLite connections were being opened and closed per project file, and database inserts (nodes and edges) were performed individually inside nested loops (`cursor.execute`). Even worse, in some source versions of `src/db.py`, the connection block exits before doing the edge inserts, causing silent failures on a closed database connection that went unnoticed due to `except Exception: pass`.
Using a single shared database connection across file walks and batching all inserts with `cursor.executemany` yields a massive performance boost (saving connection/transaction disk I/O) and guarantees transactional integrity.

**Action:**
Always batch SQL database operations using `executemany` instead of iterating with `execute`. Provide support for passing an optional shared `conn` handle in indexing/utility functions to allow single-connection batch runs across walk loops, while safely closing connections only if opened locally.

## 2026-08-15 - High-Throughput Datetime Parsing with `datetime.fromisoformat`
**Learning:**
In Python 3.11+, `datetime.strptime` involves string format parsing overhead that is over 20x slower than `datetime.fromisoformat` when processing high-volume ISO 8601 timestamps (such as GitHub comment and commit timelines). Replacing `datetime.strptime(ts.replace("Z", ""), "%Y-%m-%dT%H:%M:%S")` with `datetime.fromisoformat(ts.replace("Z", "+00:00"))` dramatically accelerates CI analytics and timeline analysis.

**Action:**
Prefer `datetime.fromisoformat` over `datetime.strptime` when parsing standard ISO 8601 date strings.
