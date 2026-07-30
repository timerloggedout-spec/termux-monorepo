#!/usr/bin/env python3
"""Agent Shell v2 – role-aware, session-contextual, tool-taxonomy-integrated.
   Imports existing components only.  Keeps all v1 features."""
import json, os, subprocess, sys, time, random
from pathlib import Path
from datetime import datetime

HOME = Path.home()

# ── Existing imports (all working) ──
sys.path.insert(0, str(HOME / 'harmony_hub' / 'workspace' / 'prompts'))
from prompt_engine import get_prompt, ROLE_TEMPLATES, PREFIXES, SUFFIXES

sys.path.insert(0, str(HOME / 'deepcli'))
from deepcli.core import get_token, create_session, chat_completion, get_history

# ── Context collector (multi-agent) ──
sys.path.insert(0, str(HOME / 'termux-multi-agent' / 'src'))
from context_collector import AutomatedContextCollector

# ── Tool Taxonomy ──
TAXONOMY_DIR = HOME / 'workspace' / 'llm_map' / '_TOOL_TAXONOMY'

# ── v1 constants ──
MASTER = HOME / 'workspace' / 'llm_map' / 'master_tasks.json'
DISPATCH = HOME / 'workspace' / 'llm_map' / 'dispatch_task.py'
TIL = HOME / 'archwiz' / 'TIL.md'
PROC = HOME / 'archwiz' / 'PROCEDURES.md'
CONS = HOME / 'archwiz' / 'CONSIDERATIONS.md'
BRANCH_DIR = HOME / 'archwiz' / 'branches'

# ── Colors ──
R = '\033[1;31m'
G = '\033[1;32m'
Y = '\033[1;33m'
C = '\033[1;36m'
N = '\033[0m'

# ── Global state ──
active_role = 'archwiz'
active_session = None
collector = AutomatedContextCollector(str(HOME))

# ── v1 features ──
def list_tasks():
    if not MASTER.exists():
        print("No master_tasks.json found.")
        return
    tasks = json.loads(MASTER.read_text())
    for t in tasks:
        status = t.get('status', '?')
        icon = {'done': '✅', 'pending': '⚡', 'failed': '❌'}.get(status, '❓')
        print(f"  {icon} {t['id']:30s} {status:8s}  {t.get('title', '')[:60]}")

def run_task(task_id):
    subprocess.run(['python3', str(DISPATCH), task_id])

def log_tag(tag, text):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M')
    mapping = {'#TIL': TIL, '#procedure': PROC, '#consideration': CONS}
    filepath = mapping.get(tag)
    if filepath:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'a') as f:
            f.write(f"\n- **[{ts}]** {text.strip()}\n")
        print(f"{G}Logged to {filepath.name}{N}")
    elif tag == '#branch':
        branch_name = text.strip().split()[0] if text.strip() else 'general'
        BRANCH_DIR.mkdir(parents=True, exist_ok=True)
        with open(BRANCH_DIR / f'{branch_name}.md', 'a') as f:
            f.write(f"\n- **[{ts}]** {text.strip()}\n")
        print(f"{G}Logged to branches/{branch_name}.md{N}")
    elif tag == '#concept':
        print(f"{Y}Running Name Forge on '{text.strip()}'...{N}")
        subprocess.run(['python3', str(HOME / 'archwiz' / 'name_forge.py'), text.strip()])

# ── v2 commands ──
def load_roles():
    roles = ROLE_TEMPLATES.copy()
    # Merge with tool taxonomy roles if available
    taxonomy_roles_file = TAXONOMY_DIR / 'roles_custom.json'
    if taxonomy_roles_file.exists():
        with open(taxonomy_roles_file) as f:
            custom = json.load(f)
            roles.update(custom)
    return roles

def list_roles_cmd():
    roles = load_roles()
    print(f"{Y}Available roles:{N}")
    for role_name, template in sorted(roles.items()):
        tool_count = len(template.get('tools', []))
        print(f"  {G}{role_name}{N} ({tool_count} tools)")

def set_role(role_name):
    global active_role
    roles = load_roles()
    if role_name not in roles:
        print(f"{R}Unknown role: {role_name}. Use 'roles' to list.{N}")
        return
    active_role = role_name
    print(f"{G}Active role set to '{active_role}'.{N}")

def show_context(file_path):
    """Display function signatures and dependents for a file."""
    try:
        sigs = collector._get_cached_signatures(Path(file_path))
        if sigs:
            print(f"{Y}Functions in {file_path}:{N}")
            for s in sigs:
                print(f"  {s}")
        else:
            print("No cached signatures available.")
        deps = collector.find_dependent_files(file_path)
        if deps:
            print(f"{Y}Dependents of {file_path}:{N}")
            for d in deps:
                print(f"  {d}")
    except Exception as e:
        print(f"{R}Context error: {e}{N}")

def session_cmd(sid):
    """Import a session and set as active context."""
    global active_session
    subprocess.run(['python3', str(HOME / 'archwiz' / 'import_session.py'), sid])
    active_session = sid
    print(f"{G}Active session set to {sid}.{N}")

def tax_cmd(query):
    """Search tool taxonomy."""
    subprocess.run(['python3', str(TAXONOMY_DIR / 'modules' / 'taxfind.py'), query])

def ask_cmd(question):
    """Send a question to DeepSeek with current role and session context."""
    if not active_session:
        print(f"{Y}No active session. Use 'session <id>' first.{N}")
        return
    try:
        token = get_token()
        # Build prompt using role
        prompt_data = get_prompt(active_role, goal=question)
        system = random.choice(PREFIXES) + prompt_data['system']
        user = prompt_data['user']
        full_prompt = f"System: {system}\n\nUser: {user}"
        print(f"{C}Sending to DeepSeek...{N}")
        # For now we just print; real version would stream via chat_completion
        # chat_completion returns the assistant response; we'd show it.
        resp = chat_completion(token, full_prompt, active_session)
        print(f"{G}Response:{N}\n{resp}")
    except Exception as e:
        print(f"{R}Ask failed: {e}{N}")

# ── Main loop (v1 + v2) ──
def main():
    print(f"{C}⚡ Agent Shell v2 – Role-Aware{N}")
    print(f"  Active role: {G}{active_role}{N}")
    print(f"  Session: {G}{active_session or 'none'}{N}")
    print("  Commands: list, run <id>, roles, role <name>, context <file>,")
    print("           session <id>, tax <query>, ask <question>")
    print("           #TIL, #procedure, #consideration, #concept, #branch")
    print("           archivist <query>, mirror, feed, exit")
    try:
        while True:
            cmd = input(f"{C}agent> {N}").strip()
            if cmd in ('exit', 'quit', 'q', 'back'):
                break
            elif cmd.startswith('#TIL '):
                log_tag('#TIL', cmd[5:])
            elif cmd.startswith('#procedure '):
                log_tag('#procedure', cmd[11:])
            elif cmd.startswith('#consideration '):
                log_tag('#consideration', cmd[14:])
            elif cmd.startswith('#concept '):
                log_tag('#concept', cmd[9:])
            elif cmd.startswith('#branch '):
                log_tag('#branch', cmd[8:])
            elif cmd == 'list':
                list_tasks()
            elif cmd.startswith('run '):
                run_task(cmd.split(' ', 1)[1])
            elif cmd.startswith('archivist '):
                subprocess.run(['python3', str(HOME / 'archwiz' / 'archivist.py')] + cmd.split()[1:])
            elif cmd == 'mirror':
                subprocess.run(['python3', str(HOME / 'archwiz' / 'mirror.py')])
            elif cmd == 'feed':
                subprocess.run(['python3', str(HOME / 'archwiz' / 'narrative.py')])
            elif cmd == 'roles':
                list_roles_cmd()
            elif cmd.startswith('role '):
                set_role(cmd.split(' ', 1)[1])
            elif cmd.startswith('context '):
                show_context(cmd.split(' ', 1)[1])
            elif cmd.startswith('session '):
                session_cmd(cmd.split(' ', 1)[1])
            elif cmd == 'session':
                print(f"{Y}Usage: session <id>  — imports a session from [13] list.{N}")
            elif cmd.startswith('tax '):
                tax_cmd(cmd.split(' ', 1)[1])
            elif cmd.startswith('ask '):
                ask_cmd(cmd.split(' ', 1)[1])
            else:
                print("Unknown command. Type 'roles' for role info.")
    except (EOFError, KeyboardInterrupt):
        print("\nExiting agent shell v2.")

if __name__ == '__main__':
    main()
