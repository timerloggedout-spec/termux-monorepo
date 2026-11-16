#!/usr/bin/env python3
"""TasQue – declare a task done by appending to ta'Done.md files."""
import sys, os, re
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
MASTER_TADONE = HOME / 'workspace/taDone.md'

# Project → ta'Done.md path mapping
PROJECT_MAP = {
    'deepcli-tui': HOME / 'workspace/deepcli-tui/taDone.md',
    'deepcli': HOME / 'workspace/deepcli/taDone.md',
    'deepseek-cli': HOME / 'workspace/deepseek-cli/taDone.md',
    'termux-multi-agent': HOME / 'workspace/termux-multi-agent/taDone.md',
    'harmony_hub': HOME / 'workspace/harmony_hub/taDone.md',
    'cli-synthegration': HOME / 'cli-synthegration/user_taDone.md',
    'archwiz': HOME / 'archwiz/taDone.md',
}

def declare(task_id: str, title: str, project: str = None, status: str = 'done'):
    """Append a TasQue entry if not already present."""
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')
    line = f"- [{now}] {task_id}: {title}\n"

    # Determine per-project file
    project_file = None
    if project:
        project_file = PROJECT_MAP.get(project)
    if not project_file:
        # Fallback: try to guess from task_id prefix or just use master
        for p, f in PROJECT_MAP.items():
            if p in task_id:
                project_file = f
                break

    # Helper to safely append if not duplicate
    def append_if_new(filepath, entry):
        if not filepath or not filepath.parent.exists():
            return
        filepath.parent.mkdir(parents=True, exist_ok=True)
        if filepath.exists():
            content = filepath.read_text()
            if task_id in content:
                return  # already declared
        with open(filepath, 'a') as f:
            f.write(entry)

    # Always write to master
    append_if_new(MASTER_TADONE, line)
    # Write to project-specific if available
    if project_file:
        append_if_new(project_file, line)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: tasque_declare.py <task_id> <title> [project]")
        sys.exit(1)
    tid = sys.argv[1]
    title = sys.argv[2]
    proj = sys.argv[3] if len(sys.argv) > 3 else None
    declare(tid, title, proj)
    print(f"🪄 TasQue declared: {tid}")
