#!/usr/bin/env python3
"""ArchWiz Dangle Detector – find broken references across all ecosystem databases."""
import json, os, sys
from pathlib import Path
from datetime import datetime

HOME = Path.home()
R = '\033[1;31m'; G = '\033[1;32m'; Y = '\033[1;33m'; C = '\033[1;36m'; N = '\033[0m'

# ── Source definitions ──────────────────────────────────────
RUN_HISTORY = HOME / 'termux-multi-agent/run_history.jsonl'
METRICS_LOG = HOME / 'workspace/llm_map/metrics_log.jsonl'
MASTER_TASKS = HOME / 'workspace/llm_map/master_tasks.json'
FORESIGHT = HOME / 'workspace/llm_map/foresight_state.json'
TASK_FILES = HOME / 'workspace/llm_map/task_files_index.json'
CORR_FILE = HOME / 'cli-synthegration/workspace/correlation/correlation_index.json'
LLM_INDEX = HOME / 'workspace/llm_map/llm_index_compact.jsonl'

def load_jsonl(path):
    if not path.exists(): return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]

def load_json(path):
    if not path.exists(): return {}
    return json.loads(path.read_text())

def load_compact(path):
    if not path.exists(): return set()
    with open(path) as f:
        return {json.loads(line)['p'] for line in f if line.strip()}

def file_exists(rel_path):
    return (HOME / rel_path).exists()

def scan():
    print(f"{C}╔════════════════════════════════════════╗")
    print(f"║   ARCHWIZ DANGLE DETECTOR             ║")
    print(f"╚════════════════════════════════════════╝{N}\n")

    issues = 0
    compact_paths = load_compact(LLM_INDEX)

    # 1. Run History: check target_file exists
    print(f"{Y}[run_history]{N}")
    rh = load_jsonl(RUN_HISTORY)
    for i, entry in enumerate(rh):
        target = entry.get('target_file', '')
        if target.startswith('task:') or target.startswith('volley:') or target.startswith('comm:') or target.startswith('smoke:') or target.startswith('cli:'):
            continue
        if target and not file_exists(target):
            print(f"  {R}✗{N} line {i}: target_file '{target}' missing on disk")
            issues += 1
    if not any(e.get('target_file') and not file_exists(e['target_file']) for e in rh):
        print(f"  {G}✓ All target files exist.{N}")

    # 2. Master Tasks: check target_file on disk
    print(f"\n{Y}[master_tasks]{N}")
    tasks = load_json(MASTER_TASKS) if MASTER_TASKS.exists() else []
    if isinstance(tasks, list):
        for t in tasks:
            tf = t.get('target_file', '')
            if tf and not tf.startswith('/') and not tf.startswith('~/'): tf = str(HOME / tf)
            if tf and not file_exists(tf.replace('~/', str(HOME)+'/')):
            if 'mailbox' in tf or 'versioning' in tf or 'ast_snippets' in tf: continue  # planned outputs
                print(f"  {R}✗{N} {t['id']}: target_file '{tf}' missing")
                issues += 1
        if not any(t.get('target_file') and not file_exists(t['target_file']) for t in tasks if isinstance(t, dict)):
            print(f"  {G}✓ All task target files exist.{N}")

    # 3. Foresight: staged files not in compact index
    print(f"\n{Y}[foresight_state]{N}")
    fs = load_json(FORESIGHT)
    staged = fs.get('staged_files', [])
    for sf in staged:
        if sf not in compact_paths:
            print(f"  {R}✗{N} staged file '{sf}' not in master index")
            issues += 1
    if not staged:
        print(f"  {G}No staged files.{N}")

    # 4. Task Files Index: files that don't exist on disk
    print(f"\n{Y}[task_files_index]{N}")
    tf_idx = load_json(TASK_FILES)
    for cat, items in tf_idx.items():
        if isinstance(items, list):
            for item in items:
                f = item if isinstance(item, str) else item.get('file') or item.get('target_file')
                if f and not file_exists(f):
                    print(f"  {R}✗{N} [{cat}] '{f}' missing")
                    issues += 1
        elif isinstance(items, dict):
            for k, v in items.items():
                f = v if isinstance(v, str) else v.get('file') or v.get('target_file')
                if f and not file_exists(f):
                    print(f"  {R}✗{N} [{cat}] '{f}' missing")
                    issues += 1

    # 5. Metrics Log: files not in compact index
    print(f"\n{Y}[metrics_log]{N}")
    ml = load_jsonl(METRICS_LOG)
    missing = 0
    for e in ml:
        f = e.get('file')
        if f and f not in compact_paths and not file_exists(f):
            missing += 1
    if missing:
        print(f"  {R}✗{N} {missing} metrics entries reference missing/un‑indexed files")
        issues += missing
    else:
        print(f"  {G}✓ All metrics files referenced in index or on disk.{N}")

    print(f"\n{C}════════════════════════════════════════{N}")
    if issues:
        print(f"{R}{issues} dangling references found.{N}")
        auto = input(f"{Y}Attempt auto‑prune? (y/n): {N}").strip().lower()
        if auto == 'y':
            prune()
    else:
        print(f"{G}✅ No dangling references found. Ecosystem healthy.{N}")

def prune():
    # Remove missing task_files_index entries
    tf_idx = load_json(TASK_FILES)
    cleaned = {}
    for cat, items in tf_idx.items():
        if isinstance(items, list):
            cleaned[cat] = [x for x in items if file_exists(x if isinstance(x, str) else x.get('file','') or x.get('target_file',''))]
        elif isinstance(items, dict):
            cleaned[cat] = {k: v for k, v in items.items() if file_exists(v if isinstance(v, str) else v.get('file','') or v.get('target_file',''))}
    TASK_FILES.write_text(json.dumps(cleaned, indent=2))
    print(f"{G}Pruned task_files_index.json{N}")

if __name__ == '__main__':
    scan()
