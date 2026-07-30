#!/usr/bin/env python3
"""The Mirror – self-critique role. Shows you what you might be missing."""
import json, os, sys, subprocess
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
MASTER = HOME / 'workspace/llm_map/master_tasks.json'
TADONE = HOME / 'workspace/taDone.md'
LEXICON = HOME / 'archwiz/lexicon.db'
G = '\033[1;32m'; Y = '\033[1;33m'; R = '\033[1;31m'; C = '\033[1;36m'; N = '\033[0m'

def reflect():
    print(f"{C}╔════════════════════════════════════════╗")
    print(f"║        🪞  THE MIRROR  🪞              ║")
    print(f"╚════════════════════════════════════════╝{N}\n")
    insights = []

    # 1. Stale tasks
    if MASTER.exists():
        tasks = json.loads(MASTER.read_text())
        pending = [t for t in tasks if t.get('status') == 'pending']
        stale = [t for t in pending if datetime.fromisoformat(t['created'].replace('Z','+00:00')).replace(tzinfo=timezone.utc) < datetime.now(timezone.utc).replace(day=datetime.now(timezone.utc).day-2)]
        if stale:
            insights.append(f"You have {len(stale)} tasks pending for >2 days.")
        missing_targets = [t for t in pending if t.get('target_file') and not (HOME / t['target_file']).exists()]
        if missing_targets:
            insights.append(f"{len(missing_targets)} pending tasks reference files that don't exist.")
    else:
        insights.append("master_tasks.json not found — no task insights.")

    # 2. Index freshness
    grid = HOME / 'workspace/llm_map/llm_index_compact.jsonl'
    if grid.exists():
        age_hours = (datetime.now().timestamp() - grid.stat().st_mtime) / 3600
        if age_hours > 48:
            insights.append(f"Grid index is {age_hours:.0f} hours old. Consider an ecosystem refresh [6].")

    # 3. Dangle check (lightweight)
    dangle = subprocess.run(['python3', str(HOME / 'archwiz/dangle_detector.py')], capture_output=True, text=True)
    if 'dangling references found' in dangle.stdout:
        count = [line for line in dangle.stdout.splitlines() if 'dangling references found' in line]
        insights.append(f"Dangle Detector: {count[0].strip() if count else 'issues found'}")

    # 4. Backup age
    backups = sorted(HOME.glob('archwiz/ecosystem_backup_*.tar.gz'), key=lambda p: p.stat().st_mtime, reverse=True)
    if backups:
        last_backup_hours = (datetime.now().timestamp() - backups[0].stat().st_mtime) / 3600
        if last_backup_hours > 72:
            insights.append(f"Last backup was {last_backup_hours:.0f} hours ago. Run [5] to backup state.")
    else:
        insights.append("No backups found. Run [5] to create one.")

    # 5. Lexicon orphan seeds
    if LEXICON.exists():
        import sqlite3
        conn = sqlite3.connect(str(LEXICON))
        seeds = conn.execute("SELECT COUNT(*) FROM terms WHERE category='seed'").fetchone()[0]
        unapproved = conn.execute("SELECT COUNT(*) FROM terms WHERE approved=0").fetchone()[0]
        if seeds:
            insights.append(f"You have {seeds} seed terms waiting to be approved or discarded.")
        if unapproved:
            insights.append(f"{unapproved} unapproved terms await review in the Lexicon Harvest [14].")
        conn.close()

    if not insights:
        print(f"{G}Everything looks sharp. No issues detected.{N}")
    else:
        for i, insight in enumerate(insights, 1):
            print(f"  {Y}{i}.{N} {insight}")

    print(f"\n{C}The Mirror fades. Your reflection is your own.{N}")

if __name__ == '__main__':
    import sys
    if '--silent' in sys.argv:
        # Silent mode: output only critical flags as plain text
        # We'll capture the reflect logic but suppress formatting
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            reflect()
        output = buf.getvalue()
        # Extract only the numbered insights as plain lines
        flags = [line.strip() for line in output.splitlines() if line.strip() and line.strip()[0].isdigit()]
        if flags:
            print('; '.join(flags))
    else:
        reflect()
