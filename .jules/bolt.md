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

## 2026-08-18 - Epoch Timestamp Caching and String Slicing for Datetime Rendering
**Learning:**
Converting file stat timestamps (`st.st_mtime`) to `time.ctime()` strings and then repeatedly back-parsing them with `time.strptime(x['mtime'], "%c")` in loops during file sorting and age filtering causes severe CPU bottlenecks in filesystem scouting. Storing the raw numeric float timestamp (`mtime_ts`) directly in entry dicts allows O(1) float comparisons. Additionally, in high-frequency rendering loops, string slicing (`timestamp[11:19]`) on fixed-width ISO date strings avoids `strptime` overhead entirely.

**Action:**
Always cache raw numeric epoch timestamps (`mtime_ts`) alongside formatted date strings during file walks, and prefer string slicing over `strptime` when extracting fixed time substrings (`HH:MM:SS`) for display.

## 2026-08-19 - Incremental File Hashing and Map-Based Fallback Resolution in Monorepo Indexing
**Learning:**
In monorepo mapping tools (`central_mapper_v420.py` & `mapper_graph.py`), computing SHA-256 hashes over every file regardless of state causes massive I/O bottlenecks during directory scanning. Reusing state-cached SHA hashes when `mtime` and `size` match avoids disk reads on unchanged files. Additionally, pre-compiling combined regex patterns and storing known filenames in an O(1) hash map for fallback import resolution eliminates repeated O(N) list scans and regex compilations per file.

**Action:**
Always check state metadata (`mtime` and `size`) before reading file contents for hashing, and construct filename lookup dictionaries once to replace linear searches during file dependency resolution.

## 2026-08-30 - Bellman-Ford Early Termination & Local Variable Caching
**Learning:**
In standard $O(V \cdot E)$ Bellman-Ford shortest-path graph search algorithms, iterating unconditionally for $V - 1$ steps causes unnecessary CPU cycles when graph distances converge early. Adding an `updated` boolean flag to track whether any edge distance was relaxed during a pass allows the algorithm to terminate early, saving up to ~95% of execution loops on typical arbitrage graphs. Additionally, caching local variable lookups (`dist_u = dist[u]`) inside the hot edge-relaxation loop eliminates dict lookup overhead.

**Action:**
Always implement early termination flags in iterative graph relaxation loops and cache dictionary lookups in local variables within high-frequency loops.
