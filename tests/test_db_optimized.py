import os
import sqlite3
import pytest
import subprocess
from src.db import init_db, index_project_file, DB_PATH

def test_db_operations(tmp_path, monkeypatch):
    # Set DB path to a temporary one
    temp_db = tmp_path / "test_repo.db"
    monkeypatch.setattr("src.db.DB_PATH", str(temp_db))

    # Initialize the DB
    init_db()

    # Check that database and tables are created
    assert temp_db.exists()
    conn = sqlite3.connect(str(temp_db))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cursor.fetchall()]
    assert "nodes" in tables
    assert "edges" in tables
    assert "run_history" in tables
    conn.close()

def test_index_project_file_no_ast_grep(tmp_path, monkeypatch):
    # Ensure no-op when ast-grep isn't there
    temp_db = tmp_path / "test_repo.db"
    monkeypatch.setattr("src.db.DB_PATH", str(temp_db))
    init_db()

    # Create a dummy python file
    test_file = tmp_path / "test_file.py"
    test_file.write_text("def test(): pass\n")

    # Since ast-grep is not installed/functional in this sandbox, it should catch Exception and pass gracefully
    # Calling index_project_file should not crash
    index_project_file(str(tmp_path), "test_file.py")

def test_index_project_file_success(tmp_path, monkeypatch):
    temp_db = tmp_path / "test_repo.db"
    monkeypatch.setattr("src.db.DB_PATH", str(temp_db))
    init_db()

    # Create dummy files
    test_file = tmp_path / "test_file.py"
    test_file.write_text("import 'os'\n")

    # Mock subprocess.check_output to return mock nodes and mock imports
    call_count = 0
    def mock_check_output(cmd, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            # Nodes
            return '[{"kind": "class", "range": {"start": {"line": 10}}, "text": "class Test"}]'
        else:
            # Imports
            return '[{"text": "import \'os\'"}]'

    monkeypatch.setattr(subprocess, "check_output", mock_check_output)

    # Call indexing
    index_project_file(str(tmp_path), "test_file.py")

    # Verify that nodes and edges are populated using executemany batch writes
    conn = sqlite3.connect(str(temp_db))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM nodes;")
    nodes = cursor.fetchall()
    assert len(nodes) == 1
    assert nodes[0][1] == "test_file.py"
    assert nodes[0][3] == "class"
    assert nodes[0][4] == "class Test"

    cursor.execute("SELECT * FROM edges;")
    edges = cursor.fetchall()
    assert len(edges) == 1
    assert edges[0][0] == "test_file.py"
    assert edges[0][1] == "os"
    conn.close()

def test_fts5_virtual_table(tmp_path, monkeypatch):
    temp_db = tmp_path / "test_repo_fts.db"
    monkeypatch.setattr("src.db.DB_PATH", str(temp_db))
    init_db()

    from src.db import batch_insert_fts_messages, search_fts_messages

    # Batch insert mock messages
    messages = [
        {"content": "How to dispatch a task into the queue", "session_id": "sess-01", "msg_idx": 1},
        {"content": "Optimizing SQLite loops with shared connections", "session_id": "sess-02", "msg_idx": 5},
        {"content": "Irrelevant content message block", "session_id": "sess-03", "msg_idx": 12}
    ]
    batch_insert_fts_messages(messages)

    # Query for "dispatch"
    results = search_fts_messages("dispatch")
    assert len(results) == 1
    assert "sess-01" in results[0][1]
    assert results[0][2] == 1
    assert "dispatch" in results[0][0]

    # Query for "SQLite"
    results = search_fts_messages("SQLite")
    assert len(results) == 1
    assert "sess-02" in results[0][1]
    assert "SQLite" in results[0][0]

def test_fuzzy_clusters_optimization(tmp_path, monkeypatch):
    import sys
    from pathlib import Path
    import time
    # Ensure cli-synthegration is in sys.path
    cli_path = str(Path(__file__).parent.parent / "cli-synthegration")
    if cli_path not in sys.path:
        sys.path.insert(0, cli_path)

    from synthegration_index import CodexIndex, MessageIndex, Pointer

    # 1. Create temporary directory structure
    base_dir = tmp_path / "codex"
    base_dir.mkdir(parents=True, exist_ok=True)
    blob_dir = base_dir / "blobs"
    blob_dir.mkdir(parents=True, exist_ok=True)

    # 2. Write message_index.json to activate fuzzy_clusters loading
    msg_index_file = base_dir / "message_index.json"
    msg_index_file.write_text('{"dummy_key": [["sess-123", "assistant", "dummy snippet", "dummy title"]]}')

    # 3. Create mock blobs with shared phrases to cluster them
    # Blobs 1 & 2 share many phrases (high similarity)
    # Blob 3 has distinct text (no/low similarity)
    # We will generate a large number of blobs to demonstrate the O(N) vs O(N^2) speedup
    blob_contents = {}

    # Generate 200 blobs to measure performance difference
    # Blobs 0-99: Category A sharing a distinct set of phrases
    # Blobs 100-199: Category B sharing a different set of phrases
    for i in range(200):
        ch = f"hash{i:03d}"
        blob_file = blob_dir / f"{ch}.blob"
        if i < 100:
            text = "the quick brown fox jumps over the lazy dog " * 5 + f"uniqueA{i}"
        else:
            text = "lorem ipsum dolor sit amet consectetur adipiscing elit " * 5 + f"uniqueB{i}"
        blob_file.write_text(text)
        blob_contents[ch] = str(blob_file)

    # 4. Initialize CodexIndex and inject our blobs
    idx = CodexIndex(base_dir)
    idx.blobs = blob_contents
    # Also initialize hash_to_pointer so reverse lookup or other dependencies won't break
    for ch in blob_contents:
        idx.hash_to_pointer[ch] = Pointer("sess-123", 0, 0, ch)

    # 5. Define original fuzzy_clusters function for side-by-side comparison
    def original_fuzzy_clusters(idx, min_shared_phrases=5):
        from pathlib import Path
        mi = MessageIndex.load(idx.base_dir)
        if not mi.inverted:
            return []
        code_phrases = {}
        for ch, blob_path in idx.blobs.items():
            if not Path(blob_path).exists():
                continue
            code = Path(blob_path).read_text()[:2000]
            words = __import__('re').findall(r'\w+', code)
            phrases = set()
            for i in range(len(words)-2):
                phrases.add(' '.join(words[i:i+3]))
            code_phrases[ch] = phrases
        clusters = {}
        hashes = list(code_phrases.keys())
        for i in range(len(hashes)):
            ch1 = hashes[i]
            phrases1 = code_phrases[ch1]
            for j in range(i+1, len(hashes)):
                ch2 = hashes[j]
                phrases2 = code_phrases[ch2]
                overlap = phrases1 & phrases2
                if len(overlap) >= min_shared_phrases:
                    canonical = min(ch1, ch2)
                    clusters.setdefault(canonical, []).append(ch2 if canonical == ch1 else ch1)
        return clusters

    # 6. Execute original and optimized algorithms and measure time
    start_orig = time.perf_counter()
    original_results = original_fuzzy_clusters(idx, min_shared_phrases=5)
    end_orig = time.perf_counter()
    time_orig = end_orig - start_orig

    start_opt = time.perf_counter()
    optimized_results = idx.fuzzy_clusters(min_shared_phrases=5)
    end_opt = time.perf_counter()
    time_opt = end_opt - start_opt

    # 7. Assert that results are exactly identical
    # Standardize the results for comparison (sorting list values)
    standardized_orig = {k: sorted(v) for k, v in original_results.items()}
    standardized_opt = {k: sorted(v) for k, v in optimized_results.items()}
    assert standardized_orig == standardized_opt

    # Check that clustering actually succeeded
    assert len(standardized_opt) > 0

    print(f"\n[Fuzzy Clusters Performance] Original: {time_orig:.6f}s | Optimized: {time_opt:.6f}s")
    print(f"[Fuzzy Clusters Speedup] {time_orig / max(time_opt, 1e-9):.2f}x faster!")
