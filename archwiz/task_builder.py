#!/usr/bin/env python3
"""Thin wrapper: collect fields → call add_task.py → optional dispatch."""
import subprocess, sys
from pathlib import Path

ADD_TASK = Path.home() / 'workspace/llm_map/add_task.py'

def main():
    print("⚡ ArchWiz Task Builder (delegates to add_task.py)")
    tid = input("Task ID: ").strip()
    if not tid:
        print("Task ID required.")
        return
    title = input("Title: ").strip() or "Untitled"
    component = input("Component [Build]: ").strip() or "Build"
    agent = input("Agent [developer]: ").strip() or "developer"
    target = input("Target file (optional): ").strip()

    cmd = ['python3', str(ADD_TASK), tid, title, component, agent]
    if target:
        cmd.append(target)
    subprocess.run(cmd)

    # Offer dispatch
    if input("Dispatch now? (y/n): ").strip().lower() == 'y':
        subprocess.run(['python3', str(Path.home() / 'workspace/llm_map/dispatch_task.py'), tid])

    # Offer to send to DeepSeek
    if input("Send to DeepSeek? (y/n): ").strip().lower() == 'y':
        prompt = f"Complete this task: {title}. Instructions: (see master_tasks.json)"
        subprocess.run(['python3', str(Path.home() / 'workspace/llm_map/deepcli_send.py'), prompt])

if __name__ == '__main__':
    main()
