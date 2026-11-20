#!/usr/bin/env python3
"""Archivist – local-only system expert. Answers questions from all indices."""
import json, os, sys, time
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
ARCHWIZ = HOME / 'archwiz'

# ── Paths to all knowledge sources ──────────────────────────
LLM_COMPACT = HOME / 'workspace/llm_map/llm_index_compact.jsonl'
FUNC_INDEX  = HOME / 'workspace/llm_map/func_index.jsonl'
MASTER_TASKS = HOME / 'workspace/llm_map/master_tasks.json'
RUN_HISTORY  = HOME / 'termux-multi-agent/run_history.jsonl'
METRICS_LOG  = HOME / 'workspace/llm_map/metrics_log.jsonl'
FORESIGHT    = HOME / 'workspace/llm_map/foresight_state.json'
ARCHAEO_STATE = ARCHWIZ / 'archaeo_state.json'
RUNNER_STATE  = ARCHWIZ / 'runner_state.json'
INDEX_REGISTRY = ARCHWIZ / 'index_registry.json'
TASQUE_FILES = [
    HOME / 'workspace/taDone.md',
    HOME / 'workspace/deepcli/taDone.md',
    HOME / 'workspace/deepcli-tui/taDone.md',
    HOME / 'workspace/termux-multi-agent/taDone.md',
    HOME / 'workspace/harmony_hub/taDone.md',
]

# ── Cache (lazy load) ───────────────────────────────────────
_cache = {}

def _load_json(path):
    if path not in _cache:
        if path.exists():
            with open(path) as f:
                _cache[path] = json.load(f)
        else:
            _cache[path] = None
    return _cache[path]

def _load_jsonl(path):
    if path not in _cache:
        if path.exists():
            with open(path) as f:
                _cache[path] = [json.loads(line) for line in f if line.strip()]
        else:
            _cache[path] = []
    return _cache[path]

def _compact_files():
    """Return set of all file paths in the master index."""
    data = _load_jsonl(LLM_COMPACT)
    return {e['p'] for e in data} if data else set()

# ── Query functions ──────────────────────────────────────────

def query_file_exists(filepath):
    """Check if a file exists on disk and in the Grid."""
    on_disk = (HOME / filepath).exists()
    in_grid = filepath in _compact_files()
    return {"on_disk": on_disk, "in_grid": in_grid}

def query_task_status(task_id):
    """Get current status of a task from master_tasks.json and taDone files."""
    tasks = _load_json(MASTER_TASKS)
    result = {"task_id": task_id, "in_master": False, "status": None, "in_tadone": False}
    if tasks:
        for t in tasks:
            if t.get('id') == task_id:
                result['in_master'] = True
                result['status'] = t.get('status')
                result['title'] = t.get('title','')
                break
    # Check all taDone files
    for tf in TASQUE_FILES:
        if tf.exists() and task_id in tf.read_text():
            result['in_tadone'] = True
            result['tadone_file'] = str(tf.relative_to(HOME))
            break
    return result

def query_last_build():
    """Return timestamps of the most recent index rebuilds."""
    info = {}
    for name, path in [
        ('grid', LLM_COMPACT),
        ('weave', FUNC_INDEX),
        ('foresight', FORESIGHT),
        ('archaeo_sweep', ARCHAEO_STATE),
        ('runner', RUNNER_STATE),
    ]:
        if path.exists():
            mtime = path.stat().st_mtime
            info[name] = datetime.fromtimestamp(mtime, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        else:
            info[name] = 'never'
    return info

def query_function_info(function_name):
    """Search for a function in the Weave (func_index.jsonl)."""
    data = _load_jsonl(FUNC_INDEX)
    matches = []
    for entry in (data or []):
        if function_name.lower() in entry.get('name', '').lower():
            matches.append({
                'name': entry['name'],
                'file': entry.get('file', '?'),
                'line': entry.get('line', '?'),
                'kind': entry.get('kind', '?'),
            })
    return matches[:20]

def query_verdicts(filepath=None, limit=20):
    """Return recent verdicts, optionally filtered by target_file."""
    data = _load_jsonl(RUN_HISTORY)
    if not data:
        return []
    if filepath:
        data = [e for e in data if e.get('target_file') == filepath]
    return data[-limit:]

def query_metrics(filepath=None, limit=10):
    """Return recent metrics entries, optionally filtered by file."""
    data = _load_jsonl(METRICS_LOG)
    if not data:
        return []
    if filepath:
        data = [e for e in data if e.get('file') == filepath]
    return data[-limit:]

def query_index_registry():
    """Return summary of all registered indices."""
    registry = _load_json(INDEX_REGISTRY)
    if not registry:
        return {"error": "No index registry found. Run the one-time generation script."}
    return {
        'total_indices': len(registry),
        'roles': sorted(set(e.get('role','unknown') for e in registry)),
        'oldest_mtime': min(e['mtime'] for e in registry),
        'newest_mtime': max(e['mtime'] for e in registry),
    }

# ── CLI ──────────────────────────────────────────────────────

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: archivist.py <query> [args]")
        print("Queries: file <path>, task <id>, last-build, func <name>, verdicts [file], metrics [file], registry")
        sys.exit(1)

    query = sys.argv[1].lower()
    arg = sys.argv[2] if len(sys.argv) > 2 else None

    if query == 'file':
        if not arg:
            print("Usage: archivist.py file <relative_path>")
            sys.exit(1)
        print(json.dumps(query_file_exists(arg), indent=2))
    elif query == 'task':
        if not arg:
            print("Usage: archivist.py task <task_id>")
            sys.exit(1)
        print(json.dumps(query_task_status(arg), indent=2))
    elif query == 'last-build':
        print(json.dumps(query_last_build(), indent=2))
    elif query == 'func':
        if not arg:
            print("Usage: archivist.py func <function_name>")
            sys.exit(1)
        for m in query_function_info(arg):
            print(f"  {m['kind']} {m['name']} @ {m['file']}:{m['line']}")
    elif query == 'verdicts':
        for v in query_verdicts(arg):
            print(f"  {v.get('timestamp','?')[:19]} | {v.get('verdict','?')} | {v.get('target_file','?')}")
    elif query == 'metrics':
        for m in query_metrics(arg):
            print(f"  {m.get('timestamp','?')[:19]} | SW:{m.get('shockwave','?')} NX:{m.get('nexus','?')} RL:{m.get('reliability','?')} | {m.get('file','?')}")
    elif query == 'registry':
        print(json.dumps(query_index_registry(), indent=2))
    else:
        print(f"Unknown query: {query}")
