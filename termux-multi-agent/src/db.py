import sqlite3
import os
import json
import re
import subprocess

DB_PATH = "local_repo.db"

def init_db():
    """
    Create the SQLite database tables used for code indexing, run history, and message search.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nodes (
                id TEXT PRIMARY KEY,
                file_path TEXT,
                language TEXT,
                type TEXT,
                name TEXT,
                start_line INTEGER
            )''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS edges (
                source_file TEXT,
                target_file TEXT,
                type TEXT,
                PRIMARY KEY (source_file, target_file, type)
            )''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS run_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_file TEXT,
                attempt_number INTEGER,
                patch_content TEXT,
                error_log TEXT,
                verdict TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
                content,
                session_id UNINDEXED,
                msg_idx UNINDEXED
            )''')
        conn.commit()
    try:
        if os.path.exists(DB_PATH):
            os.chmod(DB_PATH, 0o600)
    except Exception:
        pass

def log_attempt_telemetry(target_file, attempt, patch, errors, verdict):
    """
    Record an execution attempt and its outcome in the run history.
    
    Parameters:
    	target_file (str): Path of the file targeted by the attempt.
    	attempt (int): Attempt number.
    	patch (str): Patch content associated with the attempt.
    	errors (str): Errors recorded during the attempt.
    	verdict (str): Outcome assigned to the attempt.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO run_history (target_file, attempt_number, patch_content, error_log, verdict) VALUES (?, ?, ?, ?, ?)",
            (target_file, attempt, patch, errors, verdict)
        )
        conn.commit()

def index_project_file(workspace_root, relative_path, conn=None):
    """
    Index a supported project file and record its code nodes and import relationships.
    
    Parameters:
        workspace_root (str): Root directory containing the project file.
        relative_path (str): File path relative to the workspace root.
        conn (sqlite3.Connection, optional): Database connection to use for storing
            indexed data.
    
    Unsupported file types and indexing failures are ignored.
    """
    abs_path = os.path.join(workspace_root, relative_path)
    ext = os.path.splitext(relative_path)[1]
    lang_map = {'.py': 'python', '.js': 'javascript', '.mjs': 'javascript', '.rs': 'rust'}
    lang = lang_map.get(ext)
    if not lang:
        return
    try:
        # Run first ast-grep to scan nodes (matching specific pattern or wildcard)
        output = subprocess.check_output(
            ["ast-grep", "run", "--pattern", ".*", "--json", abs_path],
            cwd="/data/data/com.termux/files/home/termux-multi-agent",
            text=True
        )
        nodes = json.loads(output)

        # Run second ast-grep to scan imports
        import_pattern = "import $MOD from '$PATH'" if lang == 'javascript' else "import $MOD"
        import_output = subprocess.check_output(
            ["ast-grep", "run", "--pattern", import_pattern, "--json", abs_path],
            cwd="/data/data/com.termux/files/home/termux-multi-agent",
            text=True
        )
        import_nodes = json.loads(import_output)

        # Batch node database entries
        node_data = []
        for node in nodes:
            node_id = f"{relative_path}:{node.get('range', {}).get('start', {}).get('line', 0)}"
            node_data.append((
                node_id, relative_path, lang, node.get('kind'), node.get('text', '')[:50],
                node.get('range', {}).get('start', {}).get('line', 0)
            ))

        # Batch import edge database entries
        edge_data = []
        for imp in import_nodes:
            imp_text = imp.get('text', '')
            quoted_paths = re.findall(r'["\'](.*?)["\']', imp_text)
            for target in quoted_paths:
                clean_target = target.lstrip('./').replace('.js', '').replace('.py', '')
                edge_data.append((relative_path, clean_target, "imports"))

        # Database transaction using batch executemany for high performance
        close_conn = False
        if conn is None:
            conn = sqlite3.connect(DB_PATH)
            close_conn = True

        try:
            cursor = conn.cursor()
            if node_data:
                cursor.executemany("INSERT OR REPLACE INTO nodes VALUES (?, ?, ?, ?, ?, ?)", node_data)
            if edge_data:
                cursor.executemany("INSERT OR IGNORE INTO edges VALUES (?, ?, ?)", edge_data)
            if close_conn:
                conn.commit()
        finally:
            if close_conn:
                conn.close()
    except Exception:
        pass

def batch_insert_fts_messages(messages, conn=None):
    """
    Insert message records into the full-text search index.
    
    Parameters:
    	messages: Message dictionaries or tuples containing content, session ID, and message index.
    	conn: Optional SQLite database connection to use.
    """
    data = []
    for msg in messages:
        if isinstance(msg, dict):
            content = msg.get('content', '')
            session_id = msg.get('session_id', '')
            msg_idx = msg.get('msg_idx', 0)
        else:
            content, session_id, msg_idx = msg
        data.append((content, session_id, msg_idx))

    close_conn = False
    if conn is None:
        conn = sqlite3.connect(DB_PATH)
        close_conn = True
    try:
        cursor = conn.cursor()
        if data:
            cursor.executemany("INSERT INTO messages_fts(content, session_id, msg_idx) VALUES (?, ?, ?)", data)
        if close_conn:
            conn.commit()
    finally:
        if close_conn:
            conn.close()

def search_fts_messages(query, limit=10, conn=None):
    """
    Search indexed messages using an FTS5 query.
    
    Parameters:
        query: The FTS5 query expression.
        limit: Maximum number of matching messages to return.
    
    Returns:
        A list of tuples containing highlighted message snippets, session IDs, and message indexes.
    """
    close_conn = False
    if conn is None:
        conn = sqlite3.connect(DB_PATH)
        close_conn = True
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT snippet(messages_fts, 0, '<b>', '</b>', '…', 40), session_id, msg_idx FROM messages_fts WHERE content MATCH ? LIMIT ?",
            (query, limit)
        )
        return cursor.fetchall()
    finally:
        if close_conn:
            conn.close()
