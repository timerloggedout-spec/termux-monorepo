#!/usr/bin/env python3
"""Narrative Feed – the story of your ecosystem, live."""
import json, os, sys
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
R = '\033[1;31m'; G = '\033[1;32m'; Y = '\033[1;33m'; C = '\033[1;36m'; W = '\033[1;37m'; N = '\033[0m'

def load_events():
    events = []
    plog = HOME / 'archwiz/pipeline_log.jsonl'
    if plog.exists():
        with open(plog) as f:
            for line in f:
                try:
                    e = json.loads(line)
                    ts = e.get('timestamp', '')[:19]
                    verdict = e.get('verdict', e.get('type', '?'))
                    task_id = e.get('task_id', '')
                    events.append((ts, 'pipeline', f"{verdict}: {task_id}"))
                except: pass
    mlog = HOME / 'archwiz/mirror_log.jsonl'
    if mlog.exists():
        with open(mlog) as f:
            for line in f:
                try:
                    e = json.loads(line)
                    ts = e.get('timestamp', '')[:19]
                    events.append((ts, 'mirror', e.get('flags', '')[:120]))
                except: pass
    tadone = HOME / 'workspace/taDone.md'
    if tadone.exists():
        for line in tadone.read_text().splitlines():
            if line.startswith('- [20'):
                events.append((line[2:21], 'tasque', line[22:].strip()))
    # Load execution errors from pipeline log
    plog = HOME / 'archwiz/pipeline_log.jsonl'
    if plog.exists():
        with open(plog) as f:
            for line in f:
                try:
                    e = json.loads(line)
                    if e.get('type') == 'exec_error':
                        ts = e.get('timestamp', '')[:19]
                        events.append((ts, 'error', f"{e.get('error', '')[:100]}"))
                except: pass
    events.sort(key=lambda x: x[0], reverse=True)
    return events[:40]

def display():
    events = load_events()
    print(f"{C}╔════════════════════════════════════════╗")
    print(f"║        📜 NARRATIVE FEED              ║")
    print(f"╚════════════════════════════════════════╝{N}\n")
    if not events:
        print(f"{Y}No events recorded yet.{N}")
        return
    for ts, source, msg in events:
        color = {'pipeline': G, 'mirror': Y, 'runner': C, 'tasque': G}.get(source, N)
        icon = {'pipeline': '⚡', 'mirror': '🪞', 'runner': '🏃', 'tasque': '🪄', 'error': '❌'}.get(source, '•')
        print(f"  {color}{ts}  {icon} [{source}]{N}  {msg[:100]}")
    print(f"\n{C}End of feed.{N}")

if __name__ == '__main__':
    display()
