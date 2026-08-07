# Bolt's Performance Journal

Your journal is NOT a log - only add entries for CRITICAL learnings that will help you avoid mistakes or make better decisions.

## 2026-08-01 - SQLite Insert Loops and Stale Closed Connections in Multi-Agent Indexing
**Learning:**
In the multi-agent's project file indexing system, SQLite connections were being opened and closed per project file, and database inserts (nodes and edges) were performed individually inside nested loops (`cursor.execute`). Even worse, in some source versions of `src/db.py`, the connection block exits before doing the edge inserts, causing silent failures on a closed database connection that went unnoticed due to `except Exception: pass`.
Using a single shared database connection across file walks and batching all inserts with `cursor.executemany` yields a massive performance boost (saving connection/transaction disk I/O) and guarantees transactional integrity.

**Action:**
Always batch SQL database operations using `executemany` instead of iterating with `execute`. Provide support for passing an optional shared `conn` handle in indexing/utility functions to allow single-connection batch runs across walk loops, while safely closing connections only if opened locally.

## 2026-08-03 - Deferring Import-Time Direct System Exits to Prevent Test Discovery Crashes
**Learning:**
Modules containing CLI or TUI endpoints that import optional third-party libraries (such as `rich` or `curl_cffi`) should never trigger immediate `sys.exit()` or unhandled fatal exceptions at import time. Doing so will crash test suite discovery, linters, or workspace scanners even if the tests do not execute those endpoints.

**Action:**
Gracefully catch `ImportError` at the module level, set a boolean flag (e.g. `HAS_RICH = False`), and defer any required exits, warnings, or fallbacks directly to the runtime execution block (e.g., inside the `main()` function) to preserve clean and safe test collection.
