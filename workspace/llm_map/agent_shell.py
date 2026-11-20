#!/usr/bin/env python3
"""Agent Shell – ArchWiz command & knowledge center."""
import json, os, subprocess, sys, time
from pathlib import Path
from datetime import datetime

HOME = Path.home()
MASTER = HOME / 'workspace/llm_map/master_tasks.json'
DISPATCH = HOME / 'workspace/llm_map/dispatch_task.py'
TIL = HOME / 'archwiz/TIL.md'
PROC = HOME / 'archwiz/PROCEDURES.md'
CONS = HOME / 'archwiz/CONSIDERATIONS.md'
BRANCH_DIR = HOME / 'archwiz/branches'

R = '\033[1;31m'; G = '\033[1;32m'; Y = '\033[1;33m'; C = '\033[1;36m'; N = '\033[0m'

def list_tasks():
    if not MASTER.exists(): return print("No master_tasks.json found.")
    tasks = json.loads(MASTER.read_text())
    for t in tasks:
        status = t.get('status','?')
        icon = {'done':'✅','pending':'⚡','failed':'❌'}.get(status,'❓')
        print(f"  {icon} {t['id']:30s} {status:8s}  {t.get('title','')[:60]}")

def run_task(task_id):
    subprocess.run(['python3', str(DISPATCH), task_id])

def run_instruction(instruction):
    print(f"(free-form command: {instruction})")

def log_tag(tag, text):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M')
    mapping = {'#TIL': TIL, '#procedure': PROC, '#consideration': CONS}
    filepath = mapping.get(tag)
    if filepath:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'a') as f:
            f.write(f"\n- **[{ts}]** {text.strip()}\n")
        print(f"{G}Logged to {filepath.name}{N}")
    elif tag == '#branch':
        branch_name = text.strip().split()[0] if text.strip() else 'general'
        BRANCH_DIR.mkdir(parents=True, exist_ok=True)
        with open(BRANCH_DIR / f'{branch_name}.md', 'a') as f:
            f.write(f"\n- **[{ts}]** {text.strip()}\n")
        print(f"{G}Logged to branches/{branch_name}.md{N}")
    elif tag == '#concept':
        print(f"{Y}Running Name Forge on '{text.strip()}'...{N}")
        subprocess.run(['python3', str(HOME / 'archwiz/name_forge.py'), text.strip()])

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"{C}⚡ ArchWiz Agent Shell – type commands or tags:{N}")
        print("  list, run <id>, cmd <instruction>")
        print("  #TIL <insight>, #procedure <step>, #consideration <note>")
        print("  #concept <term>, #branch <name> <context>")
        print("  archivist <query>, mirror, feed, exit")
        try:
            while True:
                cmd = input(f"{C}agent> {N}").strip()
                if cmd in ('exit','quit','q'):
                    break
                if cmd.startswith('#TIL '):
                    log_tag('#TIL', cmd[5:])
                elif cmd.startswith('#procedure '):
                    log_tag('#procedure', cmd[11:])
                elif cmd.startswith('#consideration '):
                    log_tag('#consideration', cmd[14:])
                elif cmd.startswith('#concept '):
                    log_tag('#concept', cmd[9:])
                elif cmd.startswith('#branch '):
                    log_tag('#branch', cmd[8:])
                elif cmd == 'list':
                    list_tasks()
                elif cmd.startswith('run '):
                    run_task(cmd.split(' ',1)[1])
                elif cmd.startswith('archivist '):
                    subprocess.run(['python3', str(HOME / 'archwiz/archivist.py')] + cmd.split()[1:])
                elif cmd == 'mirror':
                    subprocess.run(['python3', str(HOME / 'archwiz/mirror.py')])
                elif cmd == 'feed':
                    subprocess.run(['python3', str(HOME / 'archwiz/narrative.py')])
                elif cmd.startswith('cmd '):
                    run_instruction(cmd.split(' ',1)[1])
                else:
                    print("Unknown. Try: list, run <id>, archivist <query>, mirror, feed, or #TIL / #procedure / #consideration")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting agent shell.")
    else:
        if sys.argv[1] == 'list': list_tasks()
        elif sys.argv[1] == 'run' and len(sys.argv) > 2: run_task(sys.argv[2])
        elif sys.argv[1] == 'mirror': subprocess.run(['python3', str(HOME / 'archwiz/mirror.py')])
        elif sys.argv[1] == 'feed': subprocess.run(['python3', str(HOME / 'archwiz/narrative.py')])
        else: print("Usage: agent-shell list | run <id> | mirror | feed")
