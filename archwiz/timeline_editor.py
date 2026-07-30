#!/usr/bin/env python3
"""ArchWiz Timeline Editor – with file archaeology and commit notes."""
import json, os, shutil, sys, readline
from pathlib import Path
from datetime import datetime

HOME = Path.home()
ARCHWIZ = HOME / 'archwiz'

RUN_HISTORY = HOME / 'termux-multi-agent/run_history.jsonl'
METRICS_LOG = HOME / 'workspace/llm_map/metrics_log.jsonl'
MASTER_TASKS = HOME / 'workspace/llm_map/master_tasks.json'
FORESIGHT = HOME / 'workspace/llm_map/foresight_state.json'
CORR_DIR = HOME / 'cli-synthegration/workspace/correlation'
CORR_FILE = CORR_DIR / 'correlation_index.json'
CHUNKS_DIR = CORR_DIR / 'chunks'
ARCHAEOLOGIST = HOME / 'workspace/llm_map/archaeologist.py'
COMMIT_NOTES_TOOL = HOME / 'workspace/llm_map/commit_notes.py'  # if exists

R = '\033[1;31m'; G = '\033[1;32m'; Y = '\033[1;33m'; C = '\033[1;36m'; N = '\033[0m'

def backup(path):
    if not path.exists(): return
    bak = path.with_suffix(path.suffix + '.bak')
    shutil.copy2(path, bak)
    print(f"{G}Backed up {path.name}{N}")

def load_lines(path):
    if not path.exists(): return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]

def save_lines(path, data):
    with open(path, 'w') as f:
        for entry in data:
            f.write(json.dumps(entry) + '\n')

def load_correlation():
    if (CHUNKS_DIR / 'chunks.idx.json').exists():
        import gzip
        idx = json.loads((CHUNKS_DIR / 'chunks.idx.json').read_text())
        result = {}
        for key in idx:
            chunk = CHUNKS_DIR / f"{key}.json.gz"
            if chunk.exists():
                with gzip.open(chunk, 'rt') as cf:
                    result[key] = json.load(cf)
        return result
    elif CORR_FILE.exists():
        return json.loads(CORR_FILE.read_text())
    return {}

def save_correlation(data):
    import gzip
    if CHUNKS_DIR.exists() or (CHUNKS_DIR / 'chunks.idx.json').exists():
        CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
        idx = list(data.keys())
        (CHUNKS_DIR / 'chunks.idx.json').write_text(json.dumps(idx))
        for key, val in data.items():
            chunk_path = CHUNKS_DIR / f"{key}.json.gz"
            with gzip.open(chunk_path, 'wt') as cf:
                json.dump(val, cf)
        if CORR_FILE.exists():
            CORR_FILE.rename(CORR_FILE.with_suffix('.json.bak'))
    else:
        CORR_FILE.write_text(json.dumps(data, indent=2))

def search_entries(data, term):
    results = []
    for i, entry in enumerate(data):
        if term.lower() in json.dumps(entry).lower():
            results.append((i, entry))
    return results

def edit_entry(entry):
    print(json.dumps(entry, indent=2))
    while True:
        key = input(f"{C}Key to edit (or 'done'/'delete key'): {N}").strip()
        if key.lower() == 'done':
            break
        if key.lower().startswith('delete '):
            del_key = key.split(' ',1)[1]
            if del_key in entry:
                del entry[del_key]
        elif key in entry:
            new_val = input("New value: ").strip()
            try: new_val = json.loads(new_val)
            except: pass
            entry[key] = new_val
        else:
            if input("Add new key? (y/n): ").strip().lower() == 'y':
                entry[key] = input(f"Value for '{key}': ").strip()
    return entry

def reindex():
    os.system('python3 ~/workspace/llm_map/foresight_collect.py')
    os.system('cd ~/cli-synthegration && python3 synthegration_index.py from-live-exports 2>/dev/null || echo "Correlation rebuild skipped."')

def file_archaeology():
    target = input(f"{C}File path (relative to home, e.g., deepcli-tui/tui.py): {N}").strip()
    if not target:
        return
    subprocess.run(['python3', str(ARCHAEOLOGIST), target, '--full'], check=False)

def commit_notes():
    target = input(f"{C}File path (relative to home): {N}").strip()
    if not target:
        return
    if COMMIT_NOTES_TOOL.exists():
        subprocess.run(['python3', str(COMMIT_NOTES_TOOL), target])
    else:
        print(f"{Y}Commit‑notes tool not yet built. Extracting from run_history...{N}")
        history = load_lines(RUN_HISTORY)
        matching = [e for e in history if e.get('target_file') == target]
        for e in matching[-10:]:
            print(f"  {e.get('timestamp','?')} | {e.get('verdict','?')} | {e.get('agent','?')}")

def main(json_output=False):
    while True:
        print(f"""
{C}╔════════════════════════════════════════╗
║   ARCHWIZ TIMELINE THREADER & EDITOR   ║
╚════════════════════════════════════════╝{N}
  {G}[1]{N} Run History
  {G}[2]{N} Metrics Log
  {G}[3]{N} Master Tasks
  {G}[4]{N} Foresight State
  {G}[5]{N} Correlation Index
  {G}[6]{N} Search across all stores
  {G}[7]{N} Backup & Re-index
  {G}[8]{N} Launch TUI (deepcli-tui)
  {G}[9]{N} File Archaeology Report
  {G}[10]{N} Commit Notes for File
  {G}[0]{N} Return to Dashboard
""")
        try:
            choice = input(f"{C}>> {N}").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if choice == '1':
            data = load_lines(RUN_HISTORY)
            for i, e in enumerate(data):
                print(f"  {i}: {json.dumps(e)[:120]}")
            idx = input("Entry number to edit/delete (or Enter): ").strip()
            if idx.isdigit() and int(idx) < len(data):
                entry = data[int(idx)]
                action = input("(e)dit / (d)elete: ").strip().lower()
                if action == 'e':
                    data[int(idx)] = edit_entry(entry)
                    backup(RUN_HISTORY); save_lines(RUN_HISTORY, data)
                elif action == 'd':
                    del data[int(idx)]
                    backup(RUN_HISTORY); save_lines(RUN_HISTORY, data)
        elif choice == '2':
            data = load_lines(METRICS_LOG)
            for i, e in enumerate(data):
                print(f"  {i}: {json.dumps(e)[:120]}")
            idx = input("Entry number to edit/delete: ").strip()
            if idx.isdigit() and int(idx) < len(data):
                entry = data[int(idx)]
                action = input("(e)dit / (d)elete: ").strip().lower()
                if action == 'e':
                    data[int(idx)] = edit_entry(entry)
                    backup(METRICS_LOG); save_lines(METRICS_LOG, data)
                elif action == 'd':
                    del data[int(idx)]
                    backup(METRICS_LOG); save_lines(METRICS_LOG, data)
        elif choice == '3':
            data = json.loads(MASTER_TASKS.read_text()) if MASTER_TASKS.exists() else []
            for i, t in enumerate(data):
                print(f"  {i}: {t.get('id')} | {t.get('status')} | {t.get('title','')[:60]}")
            idx = input("Task index to edit/delete: ").strip()
            if idx.isdigit() and int(idx) < len(data):
                entry = data[int(idx)]
                action = input("(e)dit / (d)elete: ").strip().lower()
                if action == 'e':
                    data[int(idx)] = edit_entry(entry)
                    backup(MASTER_TASKS); MASTER_TASKS.write_text(json.dumps(data, indent=2))
                elif action == 'd':
                    del data[int(idx)]
                    backup(MASTER_TASKS); MASTER_TASKS.write_text(json.dumps(data, indent=2))
        elif choice == '4':
            data = json.loads(FORESIGHT.read_text()) if FORESIGHT.exists() else {}
            print(json.dumps(data, indent=2))
            key = input("Key to edit: ").strip()
            if key in data:
                val = data[key]
                new_val = input("New value: ").strip()
                try: new_val = json.loads(new_val)
                except: pass
                data[key] = new_val
                backup(FORESIGHT); FORESIGHT.write_text(json.dumps(data, indent=2))
        elif choice == '5':
            try:
                data = load_correlation()
            except Exception as e:
                print(f"{R}Failed to load correlation: {e}{N}")
                continue
            if not data:
                print(f"{Y}Correlation index empty.{N}")
                continue
            keys = list(data.keys())
            print(f"Keys: {keys[:10]}...")
            key = input("Key to view/edit: ").strip()
            if key not in data:
                continue
            subdata = data[key]
            print(json.dumps(subdata, indent=2)[:1000])
            if isinstance(subdata, dict):
                subkey = input("Subkey to edit: ").strip()
                if subkey in subdata and isinstance(subdata[subkey], dict):
                    subdata[subkey] = edit_entry(subdata[subkey])
                    data[key] = subdata
                    backup(CORR_FILE); save_correlation(data)
        elif choice == '6':
            term = input("Search term: ").strip()
            stores = [
                ("run_history", load_lines(RUN_HISTORY)),
                ("metrics_log", load_lines(METRICS_LOG)),
                ("master_tasks", json.loads(MASTER_TASKS.read_text()) if MASTER_TASKS.exists() else []),
                ("foresight", [json.loads(FORESIGHT.read_text())] if FORESIGHT.exists() else [])
            ]
            for name, store in stores:
                results = search_entries(store, term)
                if results:
                    print(f"{G}{name}: {len(results)} matches{N}")
                    for idx, entry in results:
                        print(f"  {idx}: {json.dumps(entry)[:150]}")
        elif choice == '7':
            for p in [RUN_HISTORY, METRICS_LOG, MASTER_TASKS, FORESIGHT, CORR_FILE]:
                backup(p)
            print(f"{G}All databases backed up.{N}")
            reindex()
        elif choice == '8':
            os.system('deepcli-tui 2>/dev/null || echo "TUI not available"')
        elif choice == '9':
            file_archaeology()
        elif choice == '10':
            commit_notes()
        elif choice == '0':
            break

if __name__ == '__main__':
    json_flag = '--json' in sys.argv
    main(json_output=json_flag)
