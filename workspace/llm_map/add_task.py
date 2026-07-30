#!/usr/bin/env python3
"""add_task.py <id> <title> [component] [agent] [target_file]"""
import json, sys
from pathlib import Path
from datetime import datetime, timezone

if len(sys.argv) < 3:
    print("Usage: add_task.py <id> <title> [component=Build] [agent=developer] [target_file]")
    sys.exit(1)

master = Path('master_tasks.json')
tasks = json.loads(master.read_text())
tasks.append({
    "id": sys.argv[1],
    "title": sys.argv[2],
    "component": sys.argv[3] if len(sys.argv) > 3 else "Build",
    "priority": "medium",
    "assigned_agent": sys.argv[4] if len(sys.argv) > 4 else "developer",
    "account": "primary",
    "status": "pending",
    "sandbox": f"~/sandbox/{sys.argv[1]}",
    "branch_from": "root",
    "target_file": sys.argv[5] if len(sys.argv) > 5 else "",
    "instructions": "Complete this task.",
    "created": datetime.now(timezone.utc).isoformat(),
    "target_type": "source" if Path(sys.argv[5] if len(sys.argv) > 5 else "").exists() else "output"
})
master.write_text(json.dumps(tasks, indent=2))
print(f"✅ {sys.argv[1]} added")
