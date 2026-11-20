#!/usr/bin/env python3
"""Active Sprint tracking – formerly 'dangling branches' work items."""
import json, sys
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
SPRINTS_FILE = HOME / 'cli-synthegration' / 'metrics' / 'sprints.json'

SPRINTS = [
    {
        "id": "expert-unlock",
        "name": "Expert Model Unlock",
        "status": "blocked",
        "blocker": "Version header gate in WASM/JS bundle",
        "action": "Start http_sniffer.js on :8888 → set Firefox proxy → send Expert message → capture real headers",
        "branch": "Termux-CLI-Recon-and-Harmoniza → expert-investigation"
    },
    {
        "id": "similarity-chunking",
        "name": "Code Similarity Clusters",
        "status": "in-progress",
        "blocker": "0 clusters found at 60% threshold; fuzzy phrase clusters also returned 0",
        "action": "Lower threshold to 40% or use token-level Jaccard instead of 3-word phrases",
        "branch": "Termux-CLI-Recon-and-Harmoniza → 4/4-edit-continuation"
    },
    {
        "id": "dangling-conversation-branches",
        "name": "Dangling Conversation Fork Detection",
        "status": "in-progress",
        "blocker": "Syntax error fixed; depth + timestamp criteria added",
        "action": "Run `python3 ~/cli-synthegration/branch_manager.py dangling` to test",
        "branch": "Termux-CLI-Recon-and-Harmoniza → TUI-tree-analysis"
    },
    {
        "id": "agent-parallelism",
        "name": "Parallel Agent Capacity",
        "status": "active",
        "blocker": "2 concurrent tokens max per account",
        "action": "Add 2nd DeepSeek account for 4-way parallel A/B/C/D testing",
        "branch": "Termux-CLI-Recon-and-Harmoniza → 1337-team-deployment"
    },
    {
        "id": "mitmproxy-api24",
        "name": "mitmproxy on Android API 24",
        "status": "resolved",
        "resolution": "Node.js http_sniffer.js works (no native deps). Python mitmproxy wrapper failed but native libs built.",
        "branch": "Termux-CLI-Recon-and-Harmoniza → mitmproxy-api24-fix"
    },
    {
        "id": "4-4-edit-loop",
        "name": "4/4 Edit Loop Closure",
        "status": "closing",
        "resolution": "All features built. Expert capture is the final dangling branch.",
        "branch": "Termux-CLI-Recon-and-Harmoniza → 4/4-edit-continuation"
    }
]

def save():
    SPRINTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "sprints": SPRINTS
    }
    SPRINTS_FILE.write_text(json.dumps(payload, indent=2))
    return payload


def show(filter_status=None):
    sprints = []
    if SPRINTS_FILE.exists():
        try:
            sprints = json.loads(SPRINTS_FILE.read_text()).get('sprints', [])
        except:
            pass
    if not sprints:
        print('No sprints found. Run: python3 ~/cli-synthegration/sprints.py')
        return
    for s in sprints:
        icon = {'probing': '🔵', 'tuning': '🟡', 'mapped': '🟣', 'expanding': '🟢', 'resolved': '✅', 'integrating': '🏁'}.get(s.get('status',''), '❓')
        print(f'{icon} {s["name"]}')
        print(f'   Status: {s["status"]}')
        if s.get('finding'): print(f'   Finding: {s["finding"]}')
        if s.get('action'): print(f'   Next: {s["action"]}')
        if s.get('resolution'): print(f'   Resolution: {s["resolution"]}')
        if s.get('branch'): print(f'   Branch: {s["branch"]}')
        print()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        show(sys.argv[1])
    else:
        show()
    save()
