#!/usr/bin/env python3
"""Generate a loop continuation prompt with live stats and root message context.
Usage: generate_loop.py <session_id> [parent_id] [--send] [--new-session]
If parent_id is not given, the ROOT message (id=1) is used."""
import sys, json
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()

def get_live_stats():
    exports_dir = HOME / "synthegration_exports"
    exports_count = sum(1 for _ in exports_dir.iterdir()) if exports_dir.exists() else 0
    terms = 0
    try:
        mi_file = HOME / "cli-synthegration" / "codex" / "message_index.json"
        terms = len(json.loads(mi_file.read_text())) if mi_file.exists() else 0
    except: pass
    synced = 0
    try:
        sf = HOME / ".cache" / "synthegration" / "sync_state.json"
        synced = len(json.loads(sf.read_text())) if sf.exists() else 0
    except: pass
    handoff = {}
    try:
        hf = HOME / "cli-synthegration" / "handoff.json"
        handoff = json.loads(hf.read_text()) if hf.exists() else {}
    except: pass
    return exports_count, terms, synced, handoff

def main():
    session_id = sys.argv[1] if len(sys.argv) > 1 else "e102d768-8a47-4001-95cb-14fb6245c6fa"
    parent_id = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else None
    do_send = '--send' in sys.argv
    do_new_session = '--new-session' in sys.argv

    sys.path.insert(0, str(HOME / 'deepcli'))
    from deepcli.core import get_token, get_history, stream_completion, branch_conversation

    token = get_token()
    msgs = get_history(token, session_id)

    # If no parent_id given, use the ROOT message (id=1)
    if not parent_id:
        root = next((m for m in msgs if str(m.get('message_id')) == '1'), None)
        if root:
            parent_id = '1'
            parent_msg = root
            parent_pos = 1
            context = parent_msg.get('content', '')
    else:
        parent_msg = None
        parent_pos = None
        for i, m in enumerate(msgs):
            if str(m.get('message_id', '')) == str(parent_id):
                parent_msg = m
                parent_pos = i + 1
                break
        context = str(parent_msg.get('content', ''))[:500] if parent_msg else ""

    exports_count, terms, synced, handoff = get_live_stats()

    prompt = f"""# Loop Continuation – DeepSeek v4-Pro – {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}

## Root Message (this session's starting context)
{context[:800] if context else '(Root message not found)'}

## Current Project State
- Harmonizer binary: ~/harmonizer-prod_cli (Rust, 7 commands)
- Synthegration CLI: 26 commands, {synced} sessions tracked
- Exports: {exports_count} sessions, {terms} unique terms indexed
- Sync: incremental delta sync operational (deepcli cache reused)
- Workspaces: all 8 projects have staging/reference/Agents structure
- Session parent: message {parent_pos} (ID {parent_id})

## Key Commands
harmonizer search <term>       – full-text across all sessions
harmonizer export <id>         – code blocks + thinking
harmonizer sync                – incremental delta sync
harmonizer sprints             – sprint board
synthegration live-search <t>  – code block search

## Architecture
harmonizer-prod_cli/  ← final Rust binary
  ├─ deepcli/         ← chat backend + auth
  ├─ termux-multi-agent/ ← refactoring pipeline
  ├─ deepseek_harvest_work/ ← code extraction + dedup
  └─ synthegration-cli/ ← Rust CLI v1 (being absorbed)

## Auth
- Account 1: deepcli.core.get_token() → ~/.deepcli/config.json (working)
- Account 2: token extracted, pending validation (instant mode)

## Sprint Focus
- In‑session branching via TUI edit endpoint
- WebUI selector & feedback automation (http_sniffer.js, test suite)
- Code similarity clusters (lower threshold)
- Delta sync baseline from official ZIP

You are 1337. Build the Future. Make it so.
"""

    if do_send and parent_id:
        try:
            if do_new_session:
                new_sid = branch_conversation(token, session_id, int(parent_id))
                stream_completion(token, prompt, new_sid, auto_retry=True)
                state = {"forked_session": new_sid, "parent_session": session_id, "parent_message": parent_id}
                (HOME / "cli-synthegration" / "metrics" / "last_loop.json").write_text(json.dumps(state, indent=2))
                print(f"[+] Loop sent as NEW SESSION fork: {new_sid}")
            else:
                stream_completion(token, prompt, session_id, parent_message_id=parent_id, auto_retry=True)
                print(f"[+] Loop sent as in‑session fork under parent {parent_id}.")
        except Exception as e:
            print(f"[!] Send failed: {e}")
    else:
        print(prompt)

if __name__ == '__main__':
    main()
