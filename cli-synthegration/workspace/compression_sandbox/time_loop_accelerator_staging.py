#!/usr/bin/env python3
"""Time‑Loop Accelerator – manage iterative development branches.
Usage:
  time_loop_accelerator.py <session_id> [--parent <id>] [--send] [--new-session]
  time_loop_accelerator.py --list-branches
  time_loop_accelerator.py --merge-success <branch_name>

If <session_id> is omitted, the default is taken from $HARMONIZER_SESSION,
then from ~/cli-synthegration/metrics/last_loop.json, then handoff.json,
finally a hardcoded fallback.
"""
import sys, os, json
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
LOOPS_DIR = HOME / "cli-synthegration" / "metrics" / "loops"
LOOPS_DIR.mkdir(parents=True, exist_ok=True)

def _default_session():
    sid = os.environ.get("HARMONIZER_SESSION")
    if sid: return sid
    for fname in ["last_loop.json", "handoff.json"]:
        f = HOME / "cli-synthegration" / "metrics" / fname
        if f.exists():
            data = json.loads(f.read_text())
            sid = data.get("parent_session") or data.get("forked_session") or data.get("session_id")
            if sid: return sid
    return "e102d768-8a47-4001-95cb-14fb6245c6fa"   # fallback

sys.path.insert(0, str(HOME / "deepcli"))
from deepcli.core import get_token, get_history, stream_completion, branch_conversation

def get_live_stats():
    exports_dir = HOME / "synthegration_exports"
    exports_count = sum(1 for _ in exports_dir.iterdir()) if exports_dir.exists() else 0
    terms = 0
    mi_file = HOME / "cli-synthegration" / "codex" / "message_index.json"
    if mi_file.exists():
        try: terms = len(json.loads(mi_file.read_text()))
        except: pass
    synced = 0
    sf = HOME / ".cache" / "synthegration" / "sync_state.json"
    if sf.exists():
        try: synced = len(json.loads(sf.read_text()))
        except: pass
    branches = list(LOOPS_DIR.glob("*.json"))
    # leverage existing conv_branching for dangling forks
    dangling = []
    try:
        sys.path.insert(0, str(HOME / "cli-synthegration"))
        from conv_branching import BranchTracker
        bt = BranchTracker()
        dangling = bt.dangling_branches() if hasattr(bt, 'dangling_branches') else []
    except: pass
    return exports_count, terms, synced, branches, dangling

def list_branches():
    print("=== Time‑Loop Branches ===")
    for f in sorted(LOOPS_DIR.glob("*.json")):
        d = json.loads(f.read_text())
        print(f"  {f.stem}: session={d.get('forked_session','?')[:8]}  "
              f"parent={d.get('parent_message','?')}  status={d.get('status','active')}  "
              f"created={d.get('created','?')}")

def merge_success(branch_name):
    f = LOOPS_DIR / f"{branch_name}.json"
    if not f.exists():
        print(f"Branch {branch_name} not found")
        return
    data = json.loads(f.read_text())
    data["status"] = "merged"
    data["merged_at"] = datetime.now(timezone.utc).isoformat()
    f.write_text(json.dumps(data, indent=2))
    print(f"[+] Branch {branch_name} marked as MERGED → trunk")

def main():
    if '--list-branches' in sys.argv:
        list_branches()
        return
    if '--merge-success' in sys.argv:
        idx = sys.argv.index('--merge-success')
        merge_success(sys.argv[idx+1])
        return

    # session_id is first positional arg, or dynamic default
    session_id = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else _default_session()
    parent_id = None
    if '--parent' in sys.argv:
        idx = sys.argv.index('--parent')
        parent_id = sys.argv[idx+1]
    do_send = '--send' in sys.argv
    do_new_session = '--new-session' in sys.argv

    token = get_token()
    msgs = get_history(token, session_id)

    if not parent_id:
        root = next((m for m in msgs if str(m.get('message_id')) == '1'), None)
        if root:
            parent_id = '1'
            parent_pos = 1
            context = root.get('content', '')
        else:
            parent_pos = None
            context = ''
    else:
        parent_pos = None
        context = ''
        for i, m in enumerate(msgs):
            if str(m.get('message_id', '')) == str(parent_id):
                parent_pos = i + 1
                context = str(m.get('content', ''))[:500]
                break

    exports_count, terms, synced, branches, dangling = get_live_stats()

    prompt = f"""# Loop Continuation – DeepSeek v4-Pro – {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}

## Root Message Context
{context[:800] if context else '(Root message not found)'}

## Live Project State
- Harmonizer: ~/harmonizer-prod_cli (Rust, 7 commands)
- Synthegration: 26 commands, {synced} sessions tracked
- Exports: {exports_count} sessions, {terms} unique terms indexed
- Sync: delta sync operational, deepcli cache reused
- Workspaces: all 8 projects have staging/reference/Agents
- Active loop branches: {len(branches)}  Dangling forks: {len(dangling)}
- Parent: message {parent_pos} (ID {parent_id})

## Key Commands
harmonizer search <term>       – full-text search
harmonizer export <id>         – code blocks + thinking
harmonizer sync                – incremental delta sync
harmonizer sprints             – sprint board
time_loop_accelerator.py       – manage development loops

## Architecture
harmonizer-prod_cli/  ← final Rust binary
  ├─ deepcli/         ← chat backend + auth
  ├─ termux-multi-agent/ ← refactoring pipeline
  ├─ deepseek_harvest_work/ ← code extraction + dedup
  ├─ synthegration-cli/ ← Rust CLI v1 (being absorbed)
  ├─ cedarscript-editor/ ← CEDARscript tools (pip)
  └─ cedar-mcp-server.js ← MCP stdio server

## Branch Management
- Errors & refactors → loop branches (danglers)
- Successful builds → merge-success → trunk
- Tracked in ~/cli-synthegration/metrics/loops/

You are 1337. Build the Future. Make it so.
"""

    if do_send and parent_id:
        try:
            if do_new_session:
                new_sid = branch_conversation(token, session_id, int(parent_id))
                stream_completion(token, prompt, new_sid, auto_retry=True)
                state = {
                    "forked_session": new_sid,
                    "parent_session": session_id,
                    "parent_message": parent_id,
                    "status": "active",
                    "created": datetime.now(timezone.utc).isoformat()
                }
                branch_name = f"loop_{new_sid[:8]}"
                (LOOPS_DIR / f"{branch_name}.json").write_text(json.dumps(state, indent=2))
                print(f"[+] New loop branch: {branch_name} → session {new_sid[:8]}...")
            else:
                stream_completion(token, prompt, session_id, parent_message_id=parent_id, auto_retry=True)
                print(f"[+] Loop sent in‑session under parent {parent_id}.")
        except Exception as e:
            print(f"[!] Send failed: {e}")
    else:
        print(prompt)

if __name__ == '__main__':
    main()
