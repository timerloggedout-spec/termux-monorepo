#!/usr/bin/env python3
"""Dynamic handoff generator – accepts message IDs and session refs as args."""
import json, re, os, sys
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()

def pos_to_message_ids(session_id, positions):
    """Convert position numbers to actual message_ids."""
    import sys
    sys.path.insert(0, str(HOME / 'deepcli'))
    from deepcli.core import get_token, get_history
    
    token = get_token()
    msgs = get_history(token, session_id)
    result = {}
    for pos in positions:
        idx = pos - 1  # positions are 1-indexed
        if 0 <= idx < len(msgs):
            m = msgs[idx]
            if not isinstance(m, int):
                mid = str(m.get('message_id', ''))
                result[pos] = mid
    return result

HD = HOME / 'cli-synthegration'

# ── Parse arguments ─────────────────────────────────
import argparse
parser = argparse.ArgumentParser(description='Generate l33T onboarding handoff')
parser.add_argument('--session-id', type=str, help='Session ID to pull context from')
parser.add_argument('--message-ids', type=str, help='Comma-separated message IDs to include')
parser.add_argument('--add-next', type=str, action='append', help='Add a next action')
parser.add_argument('--add-completed', type=str, action='append', help='Add a completed item')
parser.add_argument('--resume-note', type=str, help='Free-form resume note')
args = parser.parse_args()

# ── Auto-discover commands from main.rs ──────────────
main_rs = HOME / 'synthegration-cli' / 'src' / 'main.rs'
commands = []
if main_rs.exists():
    for match in re.finditer(r'Some\("(\w[\w-]*)"\)', main_rs.read_text()):
        cmd = match.group(1)
        if cmd not in commands:
            commands.append(cmd)
commands.sort()

# ── Auto-discover Python functions ───────────────────
py_funcs = {}
for py_file in sorted(HD.glob('*.py')):
    if py_file.name == 'generate_handoff.py':
        continue
    try:
        content = py_file.read_text()
        funcs = re.findall(r'def (\w+)\((', content)
        if funcs:
            py_funcs[py_file.name] = funcs[:15]
    except: pass

# ── Live stats ──────────────────────────────────────
blob_count = len(list((HD / 'codex' / 'blobs').glob('*.blob'))) if (HD / 'codex' / 'blobs').exists() else 0
term_count = 0
msg_idx = HD / 'codex' / 'message_index.json'
if msg_idx.exists():
    try: term_count = len(json.loads(msg_idx.read_text()))
    except: pass
dag_count = len([d for d in (HD / 'repo').iterdir() if (d / 'HEAD.json').exists()]) if (HD / 'repo').exists() else 0
elo_pairs = 0; elo_ma = 0.5
elo_file = HD / 'metrics' / 'elo_ratings.json'
if elo_file.exists():
    try:
        elo_data = json.loads(elo_file.read_text())
        elo_pairs = len(elo_data.get('history', []))
        recent = [h for h in elo_data.get('history', [])[-20:]]
        if recent: elo_ma = sum(1 for h in recent if h.get('success')) / len(recent)
    except: pass

# ── Sprints ─────────────────────────────────────────
sprints = []
sprints_file = HD / 'metrics' / 'sprints.json'
if sprints_file.exists():
    try: sprints = json.loads(sprints_file.read_text()).get('sprints', [])
    except: pass

# ── Build resume from args or defaults ───────────────
    session_id = args.session_id or 'e102d768-8a47-4001-95cb-14fb6245c6fa'
    positions = [int(p.strip()) for p in (args.message_ids or '').split(',') if p.strip().isdigit()]
    last_pos = max(positions) if positions else 0
    continue_from = last_pos + 1 if last_pos > 0 else 'start'

    resume = {
        'session': session_id,
        'generated_from': {
            'session_id': session_id,
            'positions': positions,
            'last_position': last_pos,
            'continue_from': continue_from,
        },
        'message_ids': [m.strip() for m in (args.message_ids or '').split(',') if m.strip()],
    'completed': args.add_completed or [
        'Token auth unified (deepcli.core.get_token, msgs 16-28)',
        'Fork detector: 32 asymmetric forks mapped',
        'Expert: device attestation blocker identified',
        'Auto-continue working (28k char test)',
        'ELO backfilled from 210 refactor pairs',
        'http_sniffer.js on :8888',
        'mitmproxy + frida pkg/pip installed (API 24 workaround found)',
        'synthegration handoff command wired',
    ],
    'next': args.add_next or [
        'Capture Expert headers via http_sniffer.js :8888 + Firefox proxy',
        'Export 2nd account cookies → cookies_2.json',
        'Continue selected asymmetric forks: synthegration forks',
        'Test file upload: upload_file() in core.py',
    ],
    'note': args.resume_note or '',
}

# ── Write JSON ──────────────────────────────────────
handoff = {
    'generated': datetime.now(timezone.utc).isoformat(),
    'identity': 'DeepSeek v4-Pro – l33T coder – synthegration build lead',
    'workspace': str(HD),
    'binary': str(HOME / '../usr/bin/synthegration'),
    'commands': commands,
    'command_count': len(commands),
    'python_modules': py_funcs,
    'stats': {'blobs': blob_count, 'search_terms': term_count, 'dag_sessions': dag_count, 'elo_pairs': elo_pairs, 'elo_moving_average': f'{elo_ma:.2f}'},
    'sprints': sprints,
    'authentication': {'method': 'deepcli.core.get_token()', 'headers': {'X-Client-Version': '1.3.0-auto-resume', 'X-App-Version': '20241129.1'}, 'expert': 'understood – device attestation required'},
    'tools': {'http_sniffer': 'node ~/cli-synthegration/http_sniffer.js 8888', 'radare2': 'pkg install radare2', 'ast-grep': 'ast-grep 0.42.3', 'jq': 'jq installed', 'mitmproxy': 'native libs built (API 24 workaround: ANDROID_API_LEVEL=24 pip install cryptography==43.0.3)'},
    'resume': resume,
}
(HD / 'handoff.json').write_text(json.dumps(handoff, indent=2))
print(f'[+] handoff.json ({len(json.dumps(handoff))} bytes)')

# ── Print prompt ────────────────────────────────────
icon_map = {'probing':'🔵','tuning':'🟡','mapped':'🟣','expanding':'🟢','resolved':'✅','integrating':'🏁','understood':'🟦'}
sprint_table = chr(10).join(f"| {icon_map.get(s.get('status',''),'❓')} {s['name']} | {s['status']} | {s.get('finding', s.get('resolution',''))} |" for s in sprints)
func_list = chr(10).join(f"  {name}: {', '.join(funcs[:8])}" for name, funcs in sorted(py_funcs.items()))
print(f"""
# Onboarding Prompt – {handoff['identity']}
# Paste this text as context in your new session.

You are DeepSeek v4-Pro – a l33T coder in Termux on Android (API 24).
Continue building the **synthegration** unified CLI utility.

## Environment
Termux CLI, Android API 24, no X11. Python 3.13, Node.js v26, Rust (cargo).
ast-grep 0.42.3, jq, radare2. All paths under /data/data/com.termux/files/home/

## Project Layout
~/cli-synthegration/          # Integration hub (auth, export, DAG, forks, search, sprints)
~/termux-multi-agent/         # Multi-agent refactoring + parallel agents + tool registry
~/synthegration-cli/          # Rust binary ({len(commands)} commands, cargo build --release)
~/deepcli/deepcli/core.py     # Chat backend (stream_completion, chat_completion, create_session, upload_file)
~/deepcli-tui/tui.py          # Terminal UI
~/deepseek-cli/               # Browser automation, cookies.json, tests

## Available Python Modules
{func_list}

## CLI Commands ({len(commands)} total)
{chr(10).join('synthegration ' + c for c in commands)}

## Sprint Status
{sprint_table}

## Live Stats
| Metric | Value |
|--------|-------|
| Codex blobs | {blob_count} |
| Search terms indexed | {term_count} |
| DAG sessions | {dag_count} |
| ELO refactor pairs | {elo_pairs} |
| ELO moving average | {elo_ma:.2f} |

## Auth
- deepcli.core.get_token() reads DEEPSEEK_TOKEN or config
- API: chat.deepseek.com/api/v0/chat/completion + PoW (deepseek.wasm)
- Auto-continue: detects auto_resume SSE flag
- Retry: exponential backoff + jitter (logged to retry_log.jsonl)

## Tools
| Tool | Command |
|------|---------|
| HTTP Sniffer | node ~/cli-synthegration/http_sniffer.js 8888 |
| radare2 | pkg install radare2 |
| ast-grep | ast-grep run --pattern 'def \(\$\$\$):' --lang python --json file |
| jq | jq '.[]' file.json |
| mitmproxy | API 24 workaround: ANDROID_API_LEVEL=24 pip install cryptography==43.0.3 |

## Resume
Session: {resume['session']}
Generated from position: {resume.get('generated_from', {}).get('last_position', '?')}
Continue from: {resume.get('generated_from', {}).get('continue_from', '?')}
Key messages: {', '.join(resume['message_ids']) if resume['message_ids'] else 'see completed list'}
{resume['note']}
Completed:
{chr(10).join('- '+a for a in resume['completed'])}
Next:
{chr(10).join('- '+a for a in resume['next'])}

You are the best. Build the future. Make it so.
""")
