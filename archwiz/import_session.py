#!/usr/bin/env python3
"""Quick session import from DeepSeek API → TUI cache."""
import subprocess, sys, json, shutil
from pathlib import Path

HOME = Path.home()
CACHE_DIR = HOME / '.deepcli/session_store'
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def import_session(session_id):
    print(f"📥 Importing session {session_id}...")
    # Check if the session JSON already exists locally (TUI writes it)
    dest = CACHE_DIR / f'{session_id}.json'
    if dest.exists():
        print(f"✅ Session already cached at {dest}")
    else:
        # Fallback: try synthegration export
        result = subprocess.run(
            ['synthegration', 'export', session_id],
            capture_output=True, text=True, cwd=str(HOME / 'cli-synthegration')
        )
        if result.returncode != 0:
            result = subprocess.run(
                ['python3', str(HOME / 'cli-synthegration/synthegration_index.py'), 'export', session_id],
                capture_output=True, text=True
            )
        if result.returncode == 0:
            export_dir = HOME / 'synthegration_exports'
            for f in sorted(export_dir.glob(f'*{session_id[:8]}*'), key=lambda p: p.stat().st_mtime, reverse=True):
                if f.is_dir():
                    for jf in f.glob('*.json'):
                        shutil.copy2(jf, dest)
                        print(f"✅ Imported to {dest}")
                        break
                    break
        else:
            print(f"Export failed. Session may not be cached.")
    # Always update the active session state file
    state_file = os.path.expanduser('~/.deepcli/active_session')
    os.makedirs(os.path.dirname(state_file), exist_ok=True)
    with open(state_file, 'w') as sf:
        sf.write(session_id)
    print(f"✅ Active session set to {session_id[:16]}...")
if __name__ == '__main__':
    if len(sys.argv) < 2:
        sid = input("Session ID (or 8+ char prefix): ").strip()
    else:
        sid = sys.argv[1]
    if sid:
        import_session(sid)
