#!/usr/bin/env python3
"""
simple_agent.py – one task, one real DeepSeek call,
output → sandbox, verdict → run_history.jsonl
Uses prompt_engine.py for L33T Grimoire prompts.
"""
import json, sys, os, re
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
sys.path.insert(0, str(HOME / 'harmony_hub/workspace/prompts'))
from prompt_engine import get_prompt, PREFIXES, SUFFIXES

sys.path.insert(0, str(HOME / 'deepcli'))
from deepcli.core import chat_completion, get_token, create_session

MASTER  = HOME / 'workspace/llm_map/master_tasks.json'
RUN_HIST = HOME / 'termux-multi-agent/run_history.jsonl'

def load_tasks():
    return json.loads(MASTER.read_text())

def save_tasks(tasks):
    MASTER.write_text(json.dumps(tasks, indent=2))

def log_verdict(task_id, verdict, agent, result=''):
    entry = {
        "target_file": f"task:{task_id}",
        "verdict": verdict,
        "agent": agent,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "errors": result[:300]
    }
    RUN_HIST.parent.mkdir(parents=True, exist_ok=True)
    with open(RUN_HIST, 'a') as f:
        f.write(json.dumps(entry) + '\n')

# ── Task instructions (compact, used to build the prompt) ──
TASK_INSTRUCTIONS = {
    "arch-001": "Write a bash script that reads full_map_output.txt, runs inject_ast_hashes.py, prints summary.",
    "arch-002": "Write Python script bridge_session_ids.py that maps conv_repo sessions to message_index.json.",
    "arch-003": "Output CEDARscript patch to wire log_attempt_telemetry to also append run_history.jsonl.",
    "arch-004": "Write bash script map-query.sh with --projects, --ast-coverage, --dep-of commands.",
    "arch-005": "Output CEDARscript patch adding --fts flag to synthegration search using FTS5.",
    "arch-006": "Write bash script compress_indexes.sh to gzip large JSON files and a Python streaming reader.",
    "arch-007": "Write Python script dispatch_task.py that automates tasks from master_tasks.json through simple_agent and CEDARscript.",
    "arch-008": "Output CEDARscript patch to retrofit llm_mapper_pro.py with BatchResumer for crash‑safe scanning.",
    "arch-009": "Research .deepcli/cache: is it session data? Output CEDARscript patch to rename it to session_store.",
    "arch-010": "Write Python script gatekeeper.py that checks run_history.jsonl for PASS verdict from exact session before promotion.",
    "arch-011": "Output CEDARscript patch to deepcli-tui/tui.py adding /account toggle for primary/secondary accounts.",
}

def run_task(task_id):
    tasks = load_tasks()
    task = next((t for t in tasks if t['id'] == task_id), None)
    if not task:
        print(f"❌ Task {task_id} not found.")
        return
    if task['status'] != 'pending':
        print(f"ℹ️  Task {task_id} already {task['status']}.")
        return

    agent = task['assigned_agent']
    instructions = TASK_INSTRUCTIONS.get(task_id, "Complete the task and output only executable code or CEDARscript patches.")
    context = f"Sandbox: {task.get('sandbox','unknown')}\nComponent: {task.get('component','general')}"
    
    # Build prompt using Grimoire engine with role template
    try:
        prompt_dict = get_prompt(agent, task_title=task['title'], context=context, instructions=instructions)
        # Combine system + user for chat_completion
        prompt = f"System: {prompt_dict['system']}\n\nUser: {prompt_dict['user']}"
    except Exception:
        prompt = f"{PREFIXES[0]}\n{SUFFIXES[0]}\n\nRole: {agent}\n{task['title']}\n{context}\n{instructions}"

    task['status'] = 'in-progress'
    save_tasks(tasks)

    print(f"\n🛠️  Task {task_id}: {task['title']}")
    print(f"   Agent: {agent} | Prompt length: {len(prompt)} chars")
    print(f"   Calling DeepSeek API … (this will appear in your chat history)")

    try:
        token = get_token()
        sid = create_session(token)
        response = chat_completion(token, prompt, sid)
        success = True
        result = response
    except Exception as e:
        success = False
        result = str(e)

    sandbox = Path(task.get('sandbox', '~/sandbox/default')).expanduser()
    sandbox.mkdir(parents=True, exist_ok=True)

    (sandbox / 'llm_response.txt').write_text(result if success else f"ERROR: {result}")

    if success:
        blocks = re.findall(r'```(?:[a-zA-Z0-9+#]*)?\n?(.*?)```', result, re.DOTALL)
        if blocks:
            for i, block in enumerate(blocks):
                ext = 'txt'
                if '<<<<<<< SEARCH' in block:
                    ext = 'patch'
                elif '#!/bin/bash' in block or '#!/usr/bin/env bash' in block:
                    ext = 'sh'
                elif '#!/usr/bin/env python' in block or 'import ' in block[:50]:
                    ext = 'py'
                (sandbox / f'extracted_{i}.{ext}').write_text(block)
            print(f"   📎 Extracted {len(blocks)} code blocks")

    verdict = 'PASS' if success else 'FAIL'
    task['status'] = 'done' if success else 'failed'
    task['result'] = result[:200]
    save_tasks(tasks)
    log_verdict(task_id, verdict, agent, result)
    print(f"{'✅' if success else '❌'} Task {task_id}: {verdict}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 simple_agent.py <task_id>")
        sys.exit(1)
    run_task(sys.argv[1])
