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

from pathlib import Path
from datetime import datetime, timezone

    # Also write to run_history.jsonl for ForeSight
    rh_file = Path.home() / 'termux-multi-agent/run_history.jsonl'
    rh_file.parent.mkdir(parents=True, exist_ok=True)
    with open(rh_file, 'a') as rhf:
        json.dump({
            "target_file": target_file,
            "verdict": verdict,
            "attempt": attempt,
            "patch": patch[:200],
            "errors": errors[:200] if errors else "",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, rhf)
        rhf.write('\n')

def log_attempt_telemetry(target_file, attempt, patch, errors, verdict):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO run_history (target_file, attempt_number, patch_content, error_log, verdict) VALUES (?, ?, ?, ?, ?)",
            (target_file, attempt, patch, errors, verdict)
        )
        conn.commit()

def index_project_file(workspace_root, relative_path):
    abs_path = os.path.join(workspace_root, relative_path)
    ext = os.path.splitext(relative_path)[1]
    lang_map = {'.py': 'python', '.js': 'javascript', '.mjs': 'javascript', '.rs': 'rust'}
    lang = lang_map.get(ext)
    if not lang:
        return
    try:
        output = subprocess.check_output(["ast-grep", "scan", "--json", abs_path], text=True)
        nodes = json.loads(output)
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            for node in nodes:
                node_id = f"{relative_path}:{node.get('range', {}).get('start', {}).get('line', 0)}"
                cursor.execute(
                    "INSERT OR REPLACE INTO nodes VALUES (?, ?, ?, ?, ?, ?)",
                    (node_id, relative_path, lang, node.get('kind'), node.get('text', '')[:50],
                     node.get('range', {}).get('start', {}).get('line', 0))
                )
        import_pattern = "import $MOD from '$PATH'" if lang == 'javascript' else "import $MOD"
        import_output = subprocess.check_output(
            ["ast-grep", "scan", "--pattern", import_pattern, "--json", abs_path], text=True
        )
        import_nodes = json.loads(import_output)
        for imp in import_nodes:
            imp_text = imp.get('text', '')
            quoted_paths = re.findall(r"['"](.*?)['"]", imp_text)
            for target in quoted_paths:
                clean_target = target.lstrip('./').replace('.js', '').replace('.py', '')
                cursor.execute(
                    "INSERT OR IGNORE INTO edges VALUES (?, ?, ?)",
                    (relative_path, clean_target, "imports")
                )
        conn.commit()
    except Exception:
        pass