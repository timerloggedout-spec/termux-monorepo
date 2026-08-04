#!/usr/bin/env python3
"""ArchWiz Dashboard - consolidated, automated cockpit."""
import pathlib
import os
import subprocess
import time
import random
import sys
import json
import getpass

# Add root to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from archwiz.config import ARCHWIZ_DIR, LOG_DIR, SESSION_STORE, WORKSPACE_DIR

R = '\033[1;31m'
G = '\033[1;32m'
Y = '\033[1;33m'
C = '\033[1;36m'
W = '\033[1;37m'
N = '\033[0m'

PIPELINE_ACTIVE = False
PIPELINE_MODE = 'auto'

def banner():
    os.system('clear')
    print(C + r"""
      █████╗ ██████╗  ██████╗██╗  ██╗██╗    ██╗██╗███████╗
     ██╔══██╗██╔══██╗██╔════╝██║  ██║██║    ██║██║╚══███╔╝
     ███████║██████╔╝██║     ███████║██║ █╗ ██║██║  ███╔╝
     ██╔══██║██╔══██╗██║     ██╔══██║██║███╗██║██║ ███╔╝
     ██║  ██║██║  ██║╚██████╗██║  ██║╚███╔███╔╝██║███████╗
     ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝╚══════╝
    """ + N)
    print(f"{G}\u26a1 ARCHWIZ DASHBOARD \u26a1{N}   {time.strftime('%c')}")
    try:
        user = os.getlogin()
    except OSError:
        user = getpass.getuser()
    print(f"{W}session: {user}@{os.uname().nodename}{N}")
    print(C + "\u2500" * 60 + N)

def get_pipeline_status():
    status = f"{G}\u23fa ON{N}" if PIPELINE_ACTIVE else f"{R}\u23fb OFF{N}"
    mode_str = f"[{PIPELINE_MODE}]"
    if PIPELINE_ACTIVE:
        plog = ARCHWIZ_DIR / 'autoexec.log'
        if plog.exists():
            # Read only the last few lines instead of the whole file
            try:
                with open(plog, 'rb') as f:
                    f.seek(0, 2)  # Go to end
                    file_size = f.tell()
                    # Read up to last 2KB (roughly 20-30 lines)
                    read_size = min(2048, file_size)
                    f.seek(file_size - read_size)
                    chunk = f.read().decode('utf-8', errors='replace')
                    lines = chunk.splitlines()
                    if read_size < file_size and lines:
                        lines = lines[1:]  # drop possibly partial first line
                    for line in reversed(lines):
                        if line.strip() and '\u274c' not in line and '#' not in line:
                            last = line.strip()[:80]
                            return f"  {status} {mode_str}  |  {C}{last}{N}"
            except OSError:
                pass
    return f"  {status} {mode_str}"

def toggle_pipeline(mode=None):
    global PIPELINE_ACTIVE, PIPELINE_MODE
    if mode:
        PIPELINE_MODE = mode

    control_script = ARCHWIZ_DIR / 'listener_control.py'
    if not control_script.exists():
        print(f"{R}Error: {control_script} not found.{N}")
        return

    if PIPELINE_ACTIVE:
        result = subprocess.run(['python3', str(control_script), 'stop'])
        if result.returncode == 0:
            print(f"{R}Pipeline stopped.{N}")
            PIPELINE_ACTIVE = False
        else:
            print(f"{R}Failed to stop pipeline.{N}")
    else:
        env = os.environ.copy()
        env['ARCHWIZ_MODE'] = PIPELINE_MODE
        result = subprocess.run(['python3', str(control_script), 'start'], env=env)
        if result.returncode == 0:
            print(f"{G}Pipeline started in {PIPELINE_MODE} mode.{N}")
            PIPELINE_ACTIVE = True
        else:
            print(f"{R}Failed to start pipeline.{N}")
    time.sleep(1)

def main():
    global PIPELINE_MODE
    banner()
    print(f"  PHASE: {Y}ACTIVE{N}  MODE: {Y}CONSOLIDATED{N}")
    print(f"{get_pipeline_status()}")
    print(C + "\u2500" * 60 + N)

    while True:
        print(f"""
  {G}[1]{N} Full Autonomous Run (dispatch)
  {G}[2]{N} Diagnostic Sweep (archaeologist)
  {G}[3]{N} Agent Shell
  {G}[4]{N} Live Metrics
  {G}[5]{N} Backup State
  {G}[6]{N} Ecosystem Refresh (rebuild + sweep)
  {G}[7]{N} Manage Profiles
  {G}[8]{N} Linear Sync (novel)
  {G}[9]{N} Timeline Editor
  {G}[10]{N} Task Builder
  {G}[11]{N} Restore Version
  {G}[12]{N} Health Check (dangles + mirror)
  {G}[13]{N} Session Pipeline (import + live)
  {G}[19]{N} Promote Workspace
  {G}[a]{N} Auto Mode  |  {G}[r]{N} Review Mode  |  {G}[p]{N} Toggle Pipeline
  {G}[0]{N} Quit
""")
        try:
            choice = input(f"{C}>> {N}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break

        if choice == '0':
            break
        elif choice == '1':
            subprocess.run(['python3', str(ARCHWIZ_DIR / 'autonomous_runner.py'), '--auto-approve'])
        elif choice == '2':
            subprocess.run(['python3', str(ARCHWIZ_DIR / 'archaeo_sweep.py')])
        elif choice == '3':
            subprocess.run(['python3', str(ARCHWIZ_DIR / 'agent_shell.py')])
        elif choice == '4':
            subprocess.run(['python3', str(ARCHWIZ_DIR / 'metrics_viewer.py')])
        elif choice == '5':
            ts = time.strftime('%Y%m%d_%H%M%S')
            fname = f'ecosystem_backup_{ts}.tar.gz'
            result = subprocess.run(['tar', 'czf', fname, 'HANDOFF.json', 'master_tasks.json', 'metrics_log.jsonl', 'foresight_state.json'], cwd=str(ARCHWIZ_DIR))
            if result.returncode == 0:
                print(f"{G}Backup: {fname}{N}")
            else:
                print(f"{R}Backup failed with exit code {result.returncode}{N}")
        elif choice == '6':
            llm_map_dir = WORKSPACE_DIR / 'llm_map'
            subprocess.run(['python3', str(llm_map_dir / 'build_final_all_profile.py')])
            subprocess.run(['python3', str(llm_map_dir / 'func_indexer.py')])
            subprocess.run(['python3', str(llm_map_dir / 'foresight_collect.py')])
            subprocess.run(['python3', str(ARCHWIZ_DIR / 'archaeo_sweep.py'), '--max', '15'])
        elif choice == '7':
            prof_dir = pathlib.Path.home() / '.config' / 'llm_map' / 'profiles'
            if not prof_dir.exists():
                print(f"{Y}No profiles directory found.{N}")
            else:
                profiles = sorted(f.replace('.json', '') for f in os.listdir(prof_dir) if f.endswith('.json'))
                for idx, p in enumerate(profiles, 1):
                    print(f"  {G}[{idx}]{N} {p}")
                # Simplified for this fix
        elif choice == '8':
            subprocess.run(['python3', str(ARCHWIZ_DIR / 'linear_sync.py')])
        elif choice == '9':
            subprocess.run(['python3', str(ARCHWIZ_DIR / 'timeline_editor.py')])
        elif choice == '10':
            subprocess.run(['python3', str(ARCHWIZ_DIR / 'task_builder.py')])
        elif choice == '11':
            target = input(f"{C}File to restore (relative path): {N}").strip()
            if target:
                # Validate and normalize target path
                if target.startswith('/') or target.startswith('~') or '..' in target:
                    print(f"{R}Error: Only relative paths within workspace are allowed (no absolute paths, ~, or ..){N}")
                else:
                    subprocess.run(['python3', str(ARCHWIZ_DIR / 'restore_version.py'), target])
        elif choice == '12':
            subprocess.run(['python3', str(ARCHWIZ_DIR / 'dangle_detector.py')])
            subprocess.run(['python3', str(ARCHWIZ_DIR / 'mirror.py')])
        elif choice == '13':
            subprocess.run(['python3', str(ARCHWIZ_DIR / 'import_session.py')])
        elif choice == '19':
            subprocess.run(['python3', str(WORKSPACE_DIR / 'llm_map' / 'promote_workspace.py')])
        elif choice == 'a':
            toggle_pipeline(mode='auto')
        elif choice == 'r':
            toggle_pipeline(mode='review')
        elif choice == 'p':
            toggle_pipeline()
        
        banner()
        print(f"  PHASE: {Y}ACTIVE{N}  MODE: {Y}CONSOLIDATED{N}")
        print(f"{get_pipeline_status()}")
        print(C + "\u2500" * 60 + N)

if __name__ == "__main__":
    main()
