#!/usr/bin/env python3
"""task_runner.py — automated multi‑agent task dispatcher"""
import json, sys, subprocess, os
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
MASTER = HOME / 'workspace/llm_map/master_tasks.json'
RUN_HIST = HOME / 'termux-multi-agent/run_history.jsonl'
ORCHESTRATOR = HOME / 'termux-multi-agent/run.py'

def load_tasks():
    with open(MASTER) as f:
        return json.load(f)

def save_tasks(tasks):
    with open(MASTER, 'w') as f:
        json.dump(tasks, f, indent=2)

def log_verdict(task_id, verdict, agent, result=""):
    entry = {
        "target_file": f"task:{task_id}",
        "verdict": verdict,
        "agent": agent,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "errors": result[:200] if result else ""
    }
    RUN_HIST.parent.mkdir(parents=True, exist_ok=True)
    with open(RUN_HIST, 'a') as f:
        f.write(json.dumps(entry) + '\n')

def compose_prompt(task):
    """Use Archaeologist and Router to build a context‑rich prompt."""
    component = task.get('component', 'general')
    return f"""System: You are the {task['assigned_agent']} agent in the Caveman Ecosystem.
Task ID: {task['id']}
Component: {component}
Title: {task['title']}
Sandbox: {task.get('sandbox','')}

Instructions:
1. Research the current state of the codebase using `funcfind`, `dep`, and `archaeologist.py` as needed.
2. Implement the change in the sandbox directory.
3. Output a CEDARscript patch (SEARCH/REPLACE blocks) if modifying existing files.
4. Respond with a summary of changes and any test results.
"""

def run_task(task):
    """Execute a single task using deepcli or the orchestrator."""
    task_id = task['id']
    agent = task['assigned_agent']
    sandbox = Path(task.get('sandbox', '~/sandbox/default')).expanduser()
    sandbox.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"🛠️  Running task {task_id}: {task['title']}")
    print(f"   Agent: {agent} | Sandbox: {sandbox}")
    
    # For code‑modifying tasks, use the orchestrator
    if task.get('component') in ('Verdicts', 'Promotion', 'Automation', 'Scanner', 'TUI'):
        target_file = str(sandbox / 'target.py')
        # Create a placeholder file for the orchestrator
        target_file_path = Path(target_file)
        target_file_path.write_text(f"# Task {task_id} placeholder\n")
        # Use orchestrator's refactor pipeline
        prompt = compose_prompt(task)
        cmd = [
            'python3', str(ORCHESTRATOR),
            '--task', task_id,
            '--file', str(target_file_path.relative_to(HOME)),
            '--prompt', prompt
        ]
        try:
            result = subprocess.run(cmd, cwd=HOME, capture_output=True, text=True, timeout=120)
            output = result.stdout + result.stderr
            if 'PASS' in output.upper():
                return True, output[:500]
            else:
                return False, output[:500]
        except Exception as e:
            return False, str(e)
    else:
        # For research/docs tasks, use deepcli
        prompt = compose_prompt(task)
        try:
            result = subprocess.run(
                ['deepcli', prompt],
                cwd=HOME, capture_output=True, text=True, timeout=120
            )
            return True, result.stdout[:500] + result.stderr[:500]
        except Exception as e:
            return False, str(e)

def main():
    tasks = load_tasks()
    pending = [t for t in tasks if t['status'] == 'pending']
    
    if not pending:
        print("✅ All tasks complete.")
        return
    
    print(f"📋 {len(pending)} pending tasks found.")
    
    for task in pending:
        # Update status to in-progress
        task['status'] = 'in-progress'
        save_tasks(tasks)
        
        success, result = run_task(task)
        
        verdict = 'PASS' if success else 'FAIL'
        task['status'] = 'done' if success else 'failed'
        task['result'] = result[:200]
        save_tasks(tasks)
        log_verdict(task['id'], verdict, task['assigned_agent'], result)
        
        icon = '✅' if success else '❌'
        print(f"{icon} Task {task['id']}: {verdict}")
    
    # Show final status
    print(f"\n{'='*60}")
    print("📊 Final Status:")
    for t in tasks:
        icon = {'done': '✅', 'failed': '❌', 'pending': '⬜', 'in-progress': '🔄'}.get(t['status'], '?')
        print(f"  {icon} {t['id']}: {t['status']} [{t['assigned_agent']}]")

if __name__ == '__main__':
    main()
