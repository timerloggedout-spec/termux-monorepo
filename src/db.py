import sqlite3
import os
import json
import re
import subprocess

DB_PATH = "local_repo.db"

def init_db():
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
        conn.commit()

def log_attempt_telemetry(target_file, attempt, patch, errors, verdict):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO run_history (target_file, attempt_number, patch_content, error_log, verdict) VALUES (?, ?, ?, ?, ?)",
            (target_file, attempt, patch, errors, verdict)
        )
        conn.commit()

def index_project_file(workspace_root, relative_path, conn=None):
    abs_path = os.path.join(workspace_root, relative_path)
    ext = os.path.splitext(relative_path)[1]
    lang_map = {'.py': 'python', '.js': 'javascript', '.mjs': 'javascript', '.rs': 'rust'}
    lang = lang_map.get(ext)
    if not lang:
        return
    try:
        # Run first ast-grep to scan nodes
        output = subprocess.check_output(["ast-grep", "scan", "--json", abs_path], text=True)
        nodes = json.loads(output)

        # Run second ast-grep to scan imports
        import_pattern = "import $MOD from '$PATH'" if lang == 'javascript' else "import $MOD"
        import_output = subprocess.check_output(
            ["ast-grep", "scan", "--pattern", import_pattern, "--json", abs_path], text=True
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
            quoted_paths = re.findall(r"['"](.*?)['"]", imp_text)
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