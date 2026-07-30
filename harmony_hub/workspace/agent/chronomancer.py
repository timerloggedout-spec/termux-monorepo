#!/usr/bin/env python3
"""Chronomancer – Time-Loop fork selection and execution.

Usage:
  python3 chronomancer.py <session_id> <account> [--root] [--execute]

  --root    Fork from the very first ASSISTANT message (root of session).
            This carries forward all current tools/tokens but restarts
            the conversation fresh. Ideal for a clean-slate sprint.

  --execute Actually perform the fork (otherwise dry-run)."""

import sys, sqlite3
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path.home() / 'deepcli'))
sys.path.insert(0, str(Path.home() / 'harmony_hub/src'))
from deepcli.core import get_token, get_history, branch_conversation
from token_provider_v2 import get_token as get_token_v2

DB = Path.home() / 'termux-multi-agent/local_repo.db'

# ─────────────────────────────── helpers ───────────────────────────────

def _parse_ts(ts_str: str) -> float:
    """Parse ISO or 'YYYY-MM-DD HH:MM:SS' timestamp → epoch float."""
    clean = str(ts_str).replace('Z','+00:00')
    for fmt in (None, '%Y-%m-%d %H:%M:%S'):
        try:
            if fmt:
                dt = datetime.strptime(clean[:19], fmt)
            else:
                dt = datetime.fromisoformat(clean)
            return dt.timestamp()
        except (ValueError, TypeError):
            continue
    return 0.0

def _assistant_role(msg: dict) -> bool:
    role = (msg.get('role') or msg.get('author',{}).get('role','')).upper()
    return role == 'ASSISTANT'

# ─────────────────────────────── core ───────────────────────────────────

def find_best_fork_point(session_id: str, account: str = 'primary') -> int | None:
    """Return the message_id of the last assistant message before the
    most recent validated run for this account."""
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT session_id, timestamp FROM run_history "
        "WHERE validated=1 AND account=? "
        "ORDER BY timestamp DESC LIMIT 1",
        (account,)
    ).fetchone()
    conn.close()
    if not row:
        print("No validated run found for this account.")
        return None

    valid_ts = _parse_ts(row['timestamp'])
    token = get_token_v2(account)
    msgs = get_history(token, session_id)

    for m in reversed(msgs):
        msg_ts = _parse_ts(m.get('create_time') or m.get('inserted_at') or '')
        if _assistant_role(m) and msg_ts and msg_ts <= valid_ts:
            return int(m['message_id'])
    return None

def find_root_fork_point(session_id: str, account: str = 'primary') -> int | None:
    """Return the message_id of the FIRST assistant message."""
    token = get_token_v2(account)
    msgs = get_history(token, session_id)
    for m in msgs:
        if _assistant_role(m):
            return int(m['message_id'])
    return None

def execute_fork(session_id: str, parent_message_id: int, account: str = 'primary'):
    token = get_token_v2(account)
    new_sid = branch_conversation(token, session_id, int(parent_message_id))
    if new_sid:
        conn = sqlite3.connect(DB)
        conn.execute(
            "INSERT INTO run_history (target_file, attempt_number, patch_content, verdict, account, validated, session_id) "
            "VALUES (?,1,?,?,?,1,?)",
            ('chronomancer-fork', 'time_loop', new_sid, account)
        )
        conn.commit()
        conn.close()
        print(f'🌿 Forked: {new_sid}')
        import subprocess
        recovery = subprocess.run(
            [sys.executable, str(Path.home() / 'harmony_hub/utility_belt/recover-session.py'), session_id, '--auto'],
            capture_output=True, text=True
        )
        if recovery.stdout.strip():
            print(f'🔗 Recovery URL: {recovery.stdout.strip()}')
        return new_sid
    return None


def find_keyword_fork_point(session_id: str, keyword: str, account: str = 'primary') -> int | None:
    """Return the message_id of the assistant message that immediately precedes
    the first occurrence of 'keyword' in the session."""
    token = get_token_v2(account)
    msgs = get_history(token, session_id)
    target_parent = None
    for m in msgs:
        if keyword.lower() in (m.get('content') or '').lower():
            parent_id = m.get('parent_id')
            if parent_id:
                # Verify parent is assistant
                parent_msg = next((pm for pm in msgs if str(pm.get('message_id')) == str(parent_id)), None)
                if parent_msg and _assistant_role(parent_msg):
                    return int(parent_id)
    return None


def analyze_clusters(session_id: str, account: str = 'primary') -> dict:
    """Compare known success clusters and return the best fork strategy."""
    import difflib

    token = get_token_v2(account)

    # Account-1 success reference (hardcoded for now — will be made dynamic)
    ref_msgs = get_history(token, 'c360696e-5049-4754-9276-27d81fbe0a3e')
    ref_dict = {str(m.get('message_id')): _get_text(m) for m in ref_msgs}
    ref_cluster = ref_dict.get('114','') + '\n' + ref_dict.get('115','')

    # Current session — scan for all validated milestones
    current_msgs = get_history(token, session_id)
    curr_dict = {str(m.get('message_id')): _get_text(m) for m in current_msgs}

    # Find all confirmed messages
    confirmed_parents = []
    for mid, content in curr_dict.items():
        if 'CONFIRMED' in content and 'Account' in content:
            confirmed_parents.append(mid)

    # Build clusters around each confirmation
    clusters = {}
    for mid in confirmed_parents:
        # Get context: the assistant message before this one
        msg_obj = next((m for m in current_msgs if str(m.get('message_id')) == mid), None)
        if msg_obj:
            parent_id = str(msg_obj.get('parent_id',''))
            if parent_id in curr_dict:
                clusters[parent_id] = {
                    'parent_id': parent_id,
                    'confirmation_id': mid,
                    'similarity': difflib.SequenceMatcher(None, ref_cluster, curr_dict.get(parent_id,'')).ratio()
                }

    return {
        'reference_cluster': 'Account1-114-115',
        'clusters_found': len(clusters),
        'best_match': max(clusters.values(), key=lambda c: c['similarity']) if clusters else None,
        'all_clusters': clusters
    }

def _get_text(msg):
    content = msg.get('content','')
    if isinstance(content, dict):
        return content.get('text','')
    return content if isinstance(content, str) else ''

# ─────────────────────────────── main ───────────────────────────────────

if __name__ == '__main__':
    session_id = sys.argv[1] if len(sys.argv) > 1 else '5e116a94-8aad-486e-8e2d-ea924db07f9e'
    account = sys.argv[2] if len(sys.argv) > 2 else 'primary'
    do_root = '--root' in sys.argv
    do_analyze = '--analyze' in sys.argv

    if do_analyze:
        result = analyze_clusters(session_id, account)
        import json
        print(json.dumps(result, indent=2, default=str))
        sys.exit(0)

    do_root = '--root' in sys.argv
    do_exec = '--execute' in sys.argv
    do_keyword = '--keyword' in sys.argv
    keyword = sys.argv[sys.argv.index('--keyword') + 1] if do_keyword and sys.argv.index('--keyword') + 1 < len(sys.argv) else None

    if do_root:
        parent = find_root_fork_point(session_id, account)
    elif do_keyword and keyword:
        parent = find_keyword_fork_point(session_id, keyword, account)
    else:
        parent = find_best_fork_point(session_id, account)

    if parent:
        label = 'Root' if do_root else 'Optimal'
        print(f'{label} fork point: message {parent}')
        if do_exec:
            execute_fork(session_id, parent, account)
    else:
        print('No suitable fork point found.')
