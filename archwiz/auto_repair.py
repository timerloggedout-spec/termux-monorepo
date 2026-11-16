#!/usr/bin/env python3
"""Auto‑repair hook for simple Sentinel REVIEW issues."""
import json, subprocess, sys
from pathlib import Path

HOME = Path.home()

def attempt_fix(task_id):
    tasks = json.loads((HOME / 'workspace/llm_map/master_tasks.json').read_text())
    task = next((t for t in tasks if t['id'] == task_id), None)
    if not task: return False

    target = task.get('target_file', '')
    fixed = False

    # Fix 1: bare filename → try to find full path in Grid
    if target and '/' not in target:
        grid = HOME / 'workspace/llm_map/llm_index_compact.jsonl'
        if grid.exists():
            with open(grid) as f:
                for line in f:
                    e = json.loads(line)
                    if e['p'].endswith(target):
                        task['target_file'] = e['p']
                        fixed = True
                        break

    # Fix 2: path exists on disk but missing from Grid → add it
    if not fixed and target and (HOME / target).exists():
        # Add to Grid
        entry = {
            'p': target,
            's': (HOME / target).stat().st_size,
            'l': 'python' if target.endswith('.py') else 'unknown',
            'h': '', 'b': False, 'ah': [], 'by': 0, 'pj': 'auto'
        }
        with open(HOME / 'workspace/llm_map/llm_index_compact.jsonl', 'a') as gf:
            gf.write(json.dumps(entry) + '\n')
        fixed = True

    if fixed:
        (HOME / 'workspace/llm_map/master_tasks.json').write_text(json.dumps(tasks, indent=2))
        print(f"🔧 Auto‑repaired {task_id}: target_file → {task['target_file']}")
        return True
    return False

if __name__ == '__main__':
    if len(sys.argv) < 2: sys.exit(1)
    attempt_fix(sys.argv[1])
