#!/usr/bin/env python3
"""ArchWiz Autonomous Runner – memory‑aware, crash‑resistant task dispatcher."""
import json, os, signal, subprocess, sys, time
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
MASTER = HOME / 'workspace/llm_map/master_tasks.json'
DISPATCHER = HOME / 'workspace/llm_map/dispatch_task.py'
STATE = HOME / 'archwiz/runner_state.json'
CRASH_LOG = HOME / 'archwiz/crashes.jsonl'
MIN_FREE_MEM = 150000  # KB
COOLDOWN = 10  # seconds between tasks

R = '\033[1;31m'; G = '\033[1;32m'; Y = '\033[1;33m'; C = '\033[1;36m'; N = '\033[0m'

def log(msg):
    ts = datetime.now(timezone.utc).strftime('%H:%M:%S')
    print(f"[{ts}] {msg}")

def free_mem():
    try:
        with open('/proc/meminfo') as f:
            for line in f:
                if 'MemAvailable' in line:
                    return int(line.split()[1])
    except:
        pass
    return 999999

def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {'last_task': None, 'completed': []}

def save_state(s):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s, indent=2))

def log_crash(task_id, msg):
    entry = {
        'task_id': task_id,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'error': msg
    }
    CRASH_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(CRASH_LOG, 'a') as f:
        f.write(json.dumps(entry) + '\n')

def run_pending(watch=False, once=True):
    state = load_state()
    running = True

    def shutdown(sig, frame):
        nonlocal running
        log(f"{Y}Shutdown signal received. Finishing current task...{N}")
        running = False

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    while running:
        tasks = json.loads(MASTER.read_text()) if MASTER.exists() else []
        pending = [t for t in tasks if t.get('status') == 'pending' and t['id'] not in state['completed']]

        if not pending:
            log(f"{G}No pending tasks.{N}")
            if watch and running:
                log(f"Watching for new tasks... (Ctrl+C to stop)")
                time.sleep(COOLDOWN)
                continue
            else:
                break

        for task in pending:
            if not running:
                break
            tid = task['id']
            # Memory check
            mem = free_mem()
            while mem < MIN_FREE_MEM:
                log(f"{Y}Memory low ({mem} KB) — waiting 15s{N}")
                time.sleep(15)
                mem = free_mem()

            # 🪞 Mirror interactive guard before dispatch
            import subprocess as sp
            mirror_result = sp.run(['python3', str(HOME / 'archwiz/mirror.py')], capture_output=True, text=True)
            if mirror_result.stdout.strip():
                print(f"\n{Y}🪞 The Mirror speaks before dispatching `{tid}`:{N}")
                print(mirror_result.stdout[:500])
                if not args.auto_approve and sys.stdin.isatty():
                    if input(f"{C}Proceed with dispatch? (y/n): {N}").strip().lower() != 'y':
                        log(f"⏸️ Dispatch of {tid} paused by Mirror.")
                        continue
                else:
                    log(f"ℹ️ Auto‑approving {tid}")

            log(f"{C}⚡ Dispatching: {tid} ({task.get('title','')[:50]}){N}")
            try:
                result = subprocess.run(
                    ['python3', str(DISPATCHER), tid],
                    timeout=300  # 5 min per task max
                )
                if result.returncode == 0:
                    state['completed'].append(tid)
                    state['last_task'] = tid
                    save_state(state)
                    log(f"{G}✅ {tid} completed{N}")
                else:
                    log_crash(tid, f"Return code {result.returncode}")
                    log(f"{R}❌ {tid} failed (code {result.returncode}){N}")
            except subprocess.TimeoutExpired:
                log_crash(tid, "Timeout")
                log(f"{R}⏰ {tid} timed out{N}")
            except Exception as e:
                log_crash(tid, str(e))
                log(f"{R}💥 {tid} crashed: {e}{N}")

            time.sleep(COOLDOWN)

        if not watch:
            break

    log(f"{G}Autonomous run complete.{N}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--watch', action='store_true', help='Keep watching for new tasks')
    parser.add_argument('--once', action='store_true', default=True, help='Run once then exit')
    parser.add_argument('--auto-approve', action='store_true', help='Skip Mirror prompts')
    args = parser.parse_args()
    run_pending(watch=args.watch)
