#!/usr/bin/env python3
"""
DeepCLI TUI – persistent dashboard with tree pagination
"""
import sys, os, json, time, re
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live

console = Console()
sys.path.insert(0, str(Path.home() / "deepcli"))
from deepcli.core import (
    get_token, get_history, create_session, stream_completion,
    fetch_sessions, upload_file, wait_for_file, _cache_path,
    branch_conversation
)
import glob as _glob
import readline
import random

def _complete_file_path(text, state):
    """Tab-complete file paths for /attach."""
    if not text.startswith('/') and not text.startswith('~') and not text.startswith('.'):
        text = './' + text
    expanded = os.path.expanduser(text)
    matches = _glob.glob(expanded + '*')
    try:
        return matches[state]
    except IndexError:
        return None

# Enable tab completion after /attach
_original_completer = readline.get_completer()
def _smart_completer(text, state):
    buf = readline.get_line_buffer()
    if buf.lstrip().startswith('/attach'):
        parts = buf.split()
        if len(parts) >= 2 and not buf.endswith(' '):
            return _complete_file_path(parts[-1], state)
    if _original_completer:
        return _original_completer(text, state)
    return None
readline.set_completer(_smart_completer)
readline.parse_and_bind("tab: complete")

GOODBYES = [
    "Keep shipping. 🚀",
    "Your future self is already proud. 💪🏽",
    "Code hard, stay humble. 🌿",
    "One session closer to mastery. 🔥",
    "Rest, then build again. ⚡",
    "The terminal never truly closes. 🖥️",
    "See you in the next branch. 🌱",
    "gg wp – now go make something. 🎯",
]

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import FileHistory
    prompt_session = PromptSession(history=FileHistory(os.path.expanduser("~/.deepcli_tui_history")))
    USE_PT = True
except ImportError:
    USE_PT = False

# ─── Tree builder with line cap ───
MAX_TREE_LINES = 200

def build_tree_str(messages, selected_parent_id=None, max_depth=8, content_width=50, max_lines=200):
    total_lines = 0  # nonlocal in _render
    lines = []
    msg_map = {}
    for m in messages:
        m["_children"] = []
        msg_map[m["message_id"]] = m
    roots = []
    for m in messages:
        pid = m.get("parent_id")
        if pid and pid in msg_map:
            msg_map[pid]["_children"].append(m)
        else:
            roots.append(m)

    def _render(node, prefix="", is_last=False, depth=0):
        nonlocal total_lines
        if depth > max_depth or total_lines >= max_lines:
            if total_lines == max_lines:
                lines.append("[yellow](output truncated, /more to see full tree)[/]")
            total_lines += 1
            return
        role = node.get("role","").upper()
        mid = node.get("message_id")
        content = node.get("content","")[:content_width].replace("\n"," ")
        marker = "🔽 " if mid == selected_parent_id else ""
        connector = "└── " if is_last else "├── " if prefix else ""
        if role == "USER":
            lines.append(f"{prefix}{connector}[blue]{marker}👤 [{mid}] {content}[/]")
        else:
            lines.append(f"{prefix}{connector}[green]{marker}🤖 [{mid}] {content}[/]")
        total_lines += 1
        children = node.get("_children",[])
        for i, child in enumerate(children):
            last = (i == len(children)-1)
            new_prefix = prefix + ("   " if is_last else "│  ")
            _render(child, new_prefix, last, depth+1)

    for r in roots:
        _render(r)
    return "\n".join(lines)

def choose_message(messages, role_filter=None, label=""):
    """Pick a message, optionally filtered by role."""
    candidates = messages
    if role_filter:
        candidates = [m for m in messages if m.get("role","").upper() == role_filter.upper()]
    if not candidates:
        console.print(f"[red]No {label} messages found.[/]")
        return None
    console.print(f"[bold]Select a {label} message:[/]")
    for i, m in enumerate(candidates):
        snippet = (m.get("content","")[:60]).replace("\n"," ")
        emoji = "👤" if m.get("role","").upper() == "USER" else "🤖"
        console.print(f"  [{i}] {emoji} {snippet}")
    console.print("  [c] cancel")
    choice = input("Choice (number or c): ").strip()
    if choice.lower() == 'c':
        return None
    try:
        idx = int(choice)
        if 0 <= idx < len(candidates):
            return candidates[idx]["message_id"]
    except:
        pass
    return None


def browse_sessions(_=''):
    """Interactive session browser with real‑time category toggles."""
    # ── load all sessions with metadata ──
    all_sessions = []
    cache_dir = os.path.expanduser('~/.deepcli/session_store')
    if os.path.isdir(cache_dir):
        for f in Path(cache_dir).glob('*.json'):
            try:
                data = json.loads(f.read_text())
                msgs = data if isinstance(data, list) else data.get('messages', [])
                if msgs:
                    first = msgs[0].get('content','')[:100] if isinstance(msgs[0], dict) else str(msgs[0])[:100]
                    # auto‑detect project
                    proj = 'general'
                    for pj, keys in {'archwiz':['archwiz','cockpit','dashboard'],
                                     'deepcli':['deepcli','core.py','tui.py'],
                                     'synthegration':['synthegration','branch_manager'],
                                     'harmony_hub':['harmony_hub','token_provider'],
                                     'multi-agent':['multi-agent','orchestrator'],
                                     'cedar':['cedrlang','compression protocol'],
                                     'caveman':['caveman','disk cleanup']}.items():
                        if any(k in first.lower() for k in keys): proj = pj; break
                    is_agent = 'agent' in first.lower() or 'task' in first.lower()
                    is_test = 'test' in f.stem or 'echo' in first.lower() or len(msgs) <= 2
                    all_sessions.append({'sid':f.stem, 'msgs':len(msgs), 'snippet':first,
                                         'mtime':f.stat().st_mtime, 'proj':proj,
                                         'agent':is_agent, 'test':is_test})
            except: pass
    all_sessions.sort(key=lambda x: x['mtime'], reverse=True)

    # ── filter state ──
    show_agent = True; show_test = True; show_human = True
    proj_filter = None  # None = all
    projects = sorted(set(s['proj'] for s in all_sessions))
    per_page = 15; page = 0
    project_idx = 0  # which project is selected in the filter

    def filtered():
        return [s for s in all_sessions
                if (show_agent or not s['agent'])
                and (show_test or not s['test'])
                and (show_human or (s['agent'] or s['test']))
                and (proj_filter is None or s['proj'] == proj_filter)]

    while True:
        f = filtered()
        total = len(f)
        start = page * per_page
        page_sessions = f[start:start+per_page]

        console.clear()
        console.print(f"[bold]📂 Session Explorer – {total} sessions[/]")
        # ── filter bar ──
        agent_str = f"[{'green' if show_agent else 'red'}](A)gent[/]" 
        test_str = f"[{'green' if show_test else 'red'}](T)est[/]"
        human_str = f"[{'green' if show_human else 'red'}](H)uman[/]"
        proj_str = f"[cyan](P)roject: {proj_filter or 'all'}[/]"
        console.print(f"  {agent_str}  {test_str}  {human_str}  {proj_str}  [dim]c=clear[/]")
        console.print("─" * 60)

        for i, s in enumerate(page_sessions):
            ts = datetime.fromtimestamp(s['mtime']).strftime('%m-%d %H:%M')
            tags = []
            if s['agent']: tags.append('A')
            if s['test']: tags.append('T')
            tag_str = f" [yellow]{','.join(tags)}[/]" if tags else ""
            console.print(f"  [yellow]{start+i:3d}[/] {s['sid'][:12]}... [dim]({s['msgs']} msgs, {ts})[/] [{s['proj']}]{tag_str} {s['snippet'][:50]}")

        console.print("─" * 60)
        console.print("[dim]n=next, p=prev, A/T/H=toggle, P=cycle project, c=clear filters, q=quit[/]")
        cmd = input("> ").strip().lower()
        if cmd == 'n' and (start+per_page) < total: page += 1
        elif cmd == 'p' and page > 0: page -= 1
        elif cmd == 'q': break
        elif cmd == 'a': show_agent = not show_agent; page = 0
        elif cmd == 't': show_test = not show_test; page = 0
        elif cmd == 'h': show_human = not show_human; page = 0
        elif cmd == 'c': show_agent=show_test=show_human=True; proj_filter=None; page=0
        elif cmd == 'p' and projects:
            project_idx = (project_idx + 1) % len(projects)
            proj_filter = projects[project_idx]; page = 0
        else: pass

def prompt_session_id():
    token = get_token()
    try:
        sessions = fetch_sessions(token)
    except Exception:
        sessions = []

    if sessions:
        console.print("[bold]Recent sessions:[/]")
        table = Table(show_header=False, box=None)
        table.add_column("Num", style="bold")
        table.add_column("Title")
        table.add_column("ID", style="dim")
        for i, s in enumerate(sessions):
            sid = s.get("id") or s.get("chat_session_id")
            title = s.get("title") or s.get("name") or "(untitled)"
            table.add_row(f"[{i}]", title[:50], sid[:8] + "...")
        console.print(table)
        console.print("  [n] New session")
    else:
        console.print("No existing sessions. Creating a new one.")

    while True:
        choice = input("Select number or /new (or /help): ").strip()
        if choice.lower() in ['n', '/new']:
            return ('new', 'instant')
        if choice.lower() == '/help':
            console.print("[bold]At this stage:[/] enter a number to pick a session, or /new to start a new one.")
            continue
        if choice.lower().startswith('/browse'):
            browse_sessions(choice[7:].strip())
            continue
        if choice.lower() in ['/quit', '/exit']:
            console.print(random.choice(GOODBYES))
            sys.exit(0)
        if sessions:
            try:
                idx = int(choice)
                if 0 <= idx < len(sessions):
                    sel = sessions[idx]
                    sid = sel.get("id") or sel.get("chat_session_id")
                    mt = sel.get("model_type", "default")
                    mode = "expert" if mt == "expert" else "instant"
                    return (sid, mode)
            except:
                pass
        console.print("[red]Invalid choice.[/]")

def show_commands():
    """Display available commands with descriptions."""
    console.print(Panel("""
[bold cyan]/branches[/]       List root messages (conversation branches)
[bold cyan]/branchpoints[/]   Show fork points (messages with multiple children)
[bold cyan]/more[/]           Toggle full tree (uncapped)
[bold cyan]/flat[/]           Toggle flat/tree view
[bold cyan]/continue[/]       Pick an assistant message to continue from
[bold cyan]/edit[/]           Branch from a user message
[bold cyan]/back[/]           Return to session selection
[bold cyan]/new[/]            Create a new session
[bold cyan]/refresh[/]        Clear cache and reload
[bold cyan]/bookmark[/]       Save current position
[bold cyan]/bookmarks[/]      List saved bookmarks
[bold cyan]/thinking on|off[/] Toggle DeepThink
[bold cyan]/search on|off[/]   Toggle web search
[bold cyan]/model instant|expert[/] Switch model
[bold cyan]/attach <files> | <prompt>[/] Attach files
[bold cyan]/reset[/]          Reset to latest assistant
[bold cyan]/cmd[/]            Show this reference
""", title="Commands", expand=False))
    input("\nPress Enter to continue...")
    help_text = """
[bold]Commands:[/]
/new, /continue, /edit, /reset, /thinking on|off, /search on|off
/model expert|instant, /attach <file>, /clear-attach
/flat      – toggle flat list view
/refresh   – clear cache and reload conversation
/more      – show full tree (uncapped)
/branches  – list conversation branches
/help      – this help
exit/quit  – leave
"""
    console.print(Panel(help_text, title="Help"))
    input("\nPress Enter to continue...")

def main():
    token = get_token()
    sid, model_mode = prompt_session_id()
    if sid == 'new':
        sid = create_session(token)
        console.print(f"Created session: {sid}")

    parent_id = None
    thinking_enabled = False
    search_enabled = False
    attached_file_id = None
    attached_filename = None
    flat_view = False

    console.print("[green]Entering TUI...[/]")
    time.sleep(0.3)

    show_full_tree = False
    pending_refresh = False
    _retry_count = 0
    last_good_messages = []
    last_streamed = ""
    explicit_parent = False

    while True:
        try:
            messages = get_history(token, sid, force_refresh=True)
            if pending_refresh and (not messages or len(messages) <= len(last_good_messages)):
                # Messages haven't appeared yet – wait and keep old display
                _retry_count += 1
                if _retry_count > 10:
                    console.print("[red]Response timed out. Check DeepSeek UI.[/]")
                    pending_refresh = False
                    _retry_count = 0
                else:
                    console.clear()
                    console.print(f"[yellow]⏳ Processing response... ({_retry_count}/10)[/]")
                    tree_str = build_tree_str(last_good_messages, selected_parent_id=parent_id)
                    console.print(f"[bold]Conversation ({len(last_good_messages)} msgs)[/]\n{tree_str}")
                    console.print(status)
                    console.print(fork_info)
                    time.sleep(1.2)
                    continue
            else:
                # Reset retry count when messages arrive
                _retry_count = 0
                pending_refresh = False
            if messages:
                last_good_messages = messages
        except Exception as e:
            console.print(f"[red]Error: {e}[/]")
            time.sleep(3)
            break

        tree_str = build_tree_str(
            messages,
            selected_parent_id=parent_id,
            max_depth=8 if not show_full_tree else 99, max_lines=len(messages) if show_full_tree else 200
        )
        # show_full_tree persists until /more toggles again

        header = f"[bold]Conversation ({len(messages)} msgs)[/]\n{tree_str}"
        status = Panel(
            f"[bold]Model:[/] {'[cyan]Expert[/]' if model_mode=='expert' else '[cyan]Instant[/]'} | "
            f"[bold]Think:[/] {'[green]ON[/]' if thinking_enabled else '[red]OFF[/]'} | "
            f"[bold]Search:[/] {'[green]ON[/]' if search_enabled else '[red]OFF[/]'}",
            title="Settings", expand=False
        )
        fork_info = f"[yellow]Continuation point: {parent_id}[/]" if parent_id else "[dim]Continuing from latest[/]"

        console.clear()
        console.print(header)
        console.print(status)
        console.print(fork_info)
        if last_streamed:
            console.print(Panel(last_streamed, title="📤 Response", border_style="blue", expand=False))
            last_streamed = ""
        if last_streamed:
            console.print(Panel(last_streamed, title="📤 Last Response", border_style="blue"))
            last_streamed = ""

        try:
            if USE_PT:
                user_input = prompt_session.prompt("> ").strip()
            else:
                user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        # ── commands that don't send a message ──
        if user_input.lower() in ['exit', 'quit', '/quit']:
            console.print(random.choice(GOODBYES))
            time.sleep(0.8)
            break

        if user_input.lower().startswith('/browse'):
            args = user_input[9:].strip()
            filter_agent = '--agent' in args
            filter_test = '--test' in args
            sort_by = 'recent'
            if '--relevance' in args: sort_by = 'relevance'
            all_sessions = []
            cache_dir = os.path.expanduser('~/.deepcli/session_store')
            if os.path.isdir(cache_dir):
                for f in Path(cache_dir).glob('*.json'):
                    try:
                        data = json.loads(f.read_text())
                        msgs = data if isinstance(data, list) else data.get('messages', [])
                        if msgs:
                            first_content = msgs[0].get('content','')[:100] if isinstance(msgs[0], dict) else str(msgs[0])[:100]
                            is_agent = 'agent' in first_content.lower()
                            if filter_agent and not is_agent: continue
                            if filter_test and 'test' not in f.stem and 'echo' not in first_content: continue
                            all_sessions.append((f.stem, len(msgs), first_content, f.stat().st_mtime))
                    except: pass
            if sort_by == 'relevance':
                all_sessions.sort(key=lambda x: -x[1])  # by message count
            else:
                all_sessions.sort(key=lambda x: -x[3])  # by mtime

            page = 0; per_page = 15
            total = len(all_sessions)
            while True:
                console.clear()
                console.print(f"[bold]📂 Sessions ({total} total, {'filtered' if filter_agent or filter_test else 'all'})[/]")
                start = page * per_page
                for i, (sid, count, snippet, mtime) in enumerate(all_sessions[start:start+per_page], start=start):
                    timestamp = datetime.fromtimestamp(mtime).strftime('%m-%d %H:%M')
                    console.print(f"  [yellow]{i:3d}[/] {sid[:16]}... [dim]({count} msgs, {timestamp})[/] {snippet[:60]}")
                console.print(f"\n[dim]Page {page+1}/{(total+per_page-1)//per_page}. n=next, p=prev, q=quit[/]")
                cmd = input("> ").strip().lower()
                if cmd == 'n' and (start+per_page) < total: page += 1
                elif cmd == 'p' and page > 0: page -= 1
                elif cmd == 'q': break
                else: pass
            continue


        if user_input.lower().startswith('/diff '):
            ids = user_input[6:].strip().split()
            if len(ids) != 2:
                console.print("[red]Usage: /diff <child_id1> <child_id2>[/]")
            else:
                m1 = next((m for m in messages if m.get('message_id','') == ids[0]), None)
                m2 = next((m for m in messages if m.get('message_id','') == ids[1]), None)
                if m1 and m2:
                    c1 = m1.get('content','')
                    c2 = m2.get('content','')
                    import difflib
                    diff = difflib.unified_diff(c1.splitlines(), c2.splitlines(), fromfile=ids[0][:8], tofile=ids[1][:8], lineterm='')
                    console.print('\n'.join(list(diff)[:2000]))
                else:
                    console.print("[red]One or both message IDs not found.[/]")
            input("\nPress Enter to continue...")
            continue

        if user_input.lower() == '/back':
            # Return to session selection
            sid, model_mode = prompt_session_id()
            if sid == 'new':
                sid = create_session(token)
                console.print(f"Created session: {sid}")
            parent_id = None
            show_full_tree = False
            console.clear()
            continue
        if user_input.lower() == '/branches':
            roots = [m for m in messages if m.get("parent_id") is None and m.get("role","").upper() == "USER"]
            if not roots:
                console.print("[yellow]No branches found.[/]")
            else:
                console.print(f"[bold]🌿 {len(roots)} branches (root messages):[/]")
                for r in roots:
                    snippet = (r.get("content","")[:60]).replace("\n"," ")
                    console.print(f"  [yellow]MSG {r['message_id']}[/] {snippet}")
            input("\nPress Enter to continue...")
            continue
        if user_input.lower() == '/branchpoints':
            # Interactive fork explorer
            child_counts = {}
            for m in messages:
                pid = m.get('parent_id')
                if pid:
                    child_counts[pid] = child_counts.get(pid, 0) + 1
            forks = [(mid, count) for mid, count in child_counts.items() if count >= 2]
            if not forks:
                console.print("[yellow]No fork points found.[/]")
                input("\nPress Enter to continue...")
                continue
            forks.sort(key=lambda x: -x[1])
            page = 0
            per_page = 5
            total_pages = (len(forks) + per_page - 1) // per_page
            while True:
                console.clear()
                console.print(f"[bold]🌿 Fork Points ({len(forks)} total) — page {page+1}/{total_pages}[/]")
                console.print("─" * 60)
                start = page * per_page
                for i, (mid, count) in enumerate(forks[start:start+per_page], start=start):
                    msg = next((m for m in messages if m.get('message_id') == mid), None)
                    if not msg: continue
                    snippet = (msg.get('content','')[:80]).replace("\n"," ")
                    role = msg.get('role','?')
                    icon = "[bold cyan]👤[/]" if role.upper() == "USER" else "[bold green]🤖[/]"
                    children = [m for m in messages if m.get('parent_id') == mid]
                    # Build mini tree
                    tree_lines = []
                    for j, child in enumerate(children[:5]):
                        connector = "├──" if j < min(4, len(children)-1) else "└──"
                        c_icon = "👤" if child.get('role','').upper() == "USER" else "🤖"
                        c_snippet = (child.get('content','')[:60]).replace("\n"," ")
                        tree_lines.append(f"       {connector} {c_icon} [dim]{c_snippet}...[/]")
                    console.print(f"  {icon} [yellow]MSG {mid}[/] → [bold]{count}[/] children:")
                    console.print(f"     [italic]{snippet}[/]")
                    for line in tree_lines:
                        console.print(line)
                    if i < start+per_page-1:
                        console.print("")
                console.print("─" * 60)
                console.print("[dim]n=next page, p=prev page, q=quit[/]")
                cmd = input("> ").strip().lower()
                if cmd == 'n' and page < total_pages-1: page += 1
                elif cmd == 'p' and page > 0: page -= 1
                elif cmd == 'q': break
                else: pass
            continue
        if user_input.lower() in ('/help', '/cmd', '/commands', '/?'):
            show_commands()
            continue
        if user_input.lower().startswith('/bookmark'):
            # Save current position: session_id + parent_id
            bm_file = os.path.expanduser("~/.deepcli/bookmarks.jsonl")
            bm_entry = {
                "session_id": sid,
                "message_id": parent_id,
                "model_mode": model_mode,
                "timestamp": str(time.time())
            }
            with open(bm_file, "a") as bf:
                bf.write(json.dumps(bm_entry) + "\n")
            console.print(f"[green]🔖 Bookmarked message {parent_id}[/]")
            time.sleep(0.8)
            continue
        if user_input.lower() == '/bookmarks':
            bm_file = os.path.expanduser("~/.deepcli/bookmarks.jsonl")
            if os.path.exists(bm_file):
                console.print("[bold]🔖 Bookmarks:[/]")
                with open(bm_file) as bf:
                    for i, line in enumerate(bf):
                        if line.strip():
                            bm = json.loads(line)
                            console.print(f"  [{i}] Session: {bm.get('session_id','')[:12]}... | Msg: {bm.get('message_id','')}")
            else:
                console.print("[yellow]No bookmarks saved.[/]")
            input("\nPress Enter to continue...")
            continue
        if user_input.lower() == '/new':
            sid = create_session(token)
            parent_id = None
            attached_file_id = None
            attached_filename = None
            explicit_parent = False
            thinking_enabled = False
            search_enabled = False
            model_mode = "instant"
            console.print(f"[green]New session: {sid}[/]")
            time.sleep(1)
            continue
        if user_input.lower() == '/continue':
            new_parent = choose_message(messages, role_filter="ASSISTANT", label="assistant")
            if new_parent is not None:
                parent_id = new_parent
                console.print(f"[green]Continuing from message {parent_id}[/]")
            time.sleep(1)
            continue
        if user_input.lower() == '/edit':
            edit_target = choose_message(messages, role_filter="USER", label="user")
            if edit_target is not None:
                target_msg = next((m for m in messages if m["message_id"] == edit_target), None)
                if target_msg:
                    # Branch from the parent of the selected user message
                    parent_id = target_msg.get("parent_id")  # None for root → new branch
                    explicit_parent = True
                    if parent_id is None:
                        console.print(f"[green]🌿 New root branch from message {edit_target}[/]")
                    else:
                        console.print(f"[green]🌿 Branch under message {parent_id}[/]")
            time.sleep(1)
            continue

        if user_input.lower() == '/reset':
            parent_id = None
            console.print("[green]Reset to latest assistant.[/]")
            time.sleep(1)
            continue
        if user_input.lower().startswith('/thinking '):
            val = user_input.split()[1].lower()
            thinking_enabled = val in ['on', 'true', '1']
            time.sleep(0.3)
            continue
        if user_input.lower().startswith('/search '):
            val = user_input.split()[1].lower()
            search_enabled = val in ['on', 'true', '1']
            time.sleep(0.3)
            continue
        if user_input.lower().startswith('/model '):
            val = user_input.split()[1].lower()
            if val in ['expert', 'pro']:
                model_mode = 'expert'
            elif val in ['instant', 'default']:
                model_mode = 'instant'
            console.print(f"[yellow]Model set to {model_mode}.[/]")
            time.sleep(0.3)
            continue
        if user_input.lower().startswith('/attach '):
            # Format: /attach <file1> [<file2> ...] | <prompt>
            args = user_input[7:].strip()
            if not args:
                console.print("[red]Usage: /attach <file...> | <prompt>[/]")
                continue
            # Split on | to separate files and prompt
            if '|' in args:
                file_part, prompt_part = args.split('|', 1)
                file_part = file_part.strip()
                prompt_part = prompt_part.strip()
            else:
                file_part = args
                prompt_part = None

            # Parse file paths (space-separated, allow quotes)
            import shlex
            try:
                file_paths = shlex.split(file_part)
            except ValueError:
                file_paths = file_part.split()

            valid_fids = []
            for fp in file_paths:
                fp = os.path.expanduser(fp.strip())
                if not Path(fp).exists():
                    console.print(f"[red]File not found: {fp}[/]")
                    continue
                console.print(f"[yellow]Uploading {fp}...[/]")
                try:
                    fid = upload_file(token, sid, fp)
                except Exception as e:
                    console.print(f"[red]Upload error: {e}[/]")
                    continue
                if fid:
                    wait_for_file(token, fid)
                    valid_fids.append(fid)
                    console.print(f"[green]Attached: {Path(fp).name} (ID: {fid})[/]")
                else:
                    console.print(f"[red]Upload failed (no ID returned): {fp}[/]")
            if valid_fids:
                attached_file_id = valid_fids if len(valid_fids) > 1 else valid_fids[0]
                attached_filename = ", ".join(Path(fp).name for fp in file_paths)
            if prompt_part:
                user_input = prompt_part
                # Fall through to send
            else:
                time.sleep(0.5)
                continue
        if user_input.lower() == '/clear-attach':
            attached_file_id = None
            attached_filename = None
            explicit_parent = False
            console.print("[green]Attachment cleared.[/]")
            time.sleep(0.3)
            continue
        if user_input.lower() == '/flat':
            flat_view = not flat_view
            console.print(f"[yellow]Tree view: {'flat' if flat_view else 'tree'}[/]")
            time.sleep(0.5)
            continue
        if user_input.lower() == '/refresh':
            cache_file = _cache_path(sid)
            if os.path.exists(cache_file):
                os.remove(cache_file)
                console.print("[green]Cache cleared. Refreshing...[/]")
            show_full_tree = False
            time.sleep(0.5)
            continue
        if user_input.lower() == '/more':
            show_full_tree = not show_full_tree
            status_msg = "ON" if show_full_tree else "OFF"
            console.print(f"[yellow]Full tree: {status_msg} (uncapped)[/]")
            time.sleep(0.8)
            continue
        if user_input.lower() == '/dangle':
            all_ids = {m["message_id"] for m in messages}
            orphans = [m for m in messages if m.get("parent_id") and m["parent_id"] not in all_ids]
            if orphans:
                console.print(f"[bold red]❌ {len(orphans)} dangling messages:[/]")
                for o in orphans[:20]:
                    console.print(f"  • {o['message_id'][:16]}… parent {o['parent_id'][:16]}… ({o.get('role','?')})")
            else:
                console.print("[green]No dangling messages.[/]")
            time.sleep(1)
            continue
        if user_input.startswith('/'):
            console.print(f"[red]Unknown command: {user_input}. Type /help for list.[/]")
            time.sleep(0.5)
            continue
        if not user_input:
            continue

        # ── send message ──
        try:
            console.print("[yellow]Sending...[/]")
            actual_parent = parent_id
            if actual_parent is None and not explicit_parent:
                assistants = [m for m in messages if m.get("role","").upper() == "ASSISTANT"]
                if assistants:
                    actual_parent = assistants[-1]["message_id"]

            file_ids = []
            if attached_file_id:
                file_ids = attached_file_id if isinstance(attached_file_id, list) else [attached_file_id]
            stream_completion(token, user_input, sid, actual_parent,
                              thinking=thinking_enabled,
                              search=search_enabled,
                              file_ids=file_ids)
            attached_file_id = None
            attached_filename = None
            explicit_parent = False
            pending_refresh = True
            _retry_count = 0
        except Exception as e:
            console.print(f"[red]Send failed: {e}[/]")
            attached_file_id = None
            attached_filename = None
            explicit_parent = False

        except Exception as e:
            console.print(f"[red]Send failed: {e}[/]")
            attached_file_id = None
            attached_filename = None
            explicit_parent = False
            time.sleep(2)   # keep error visible
        try:
            get_history(token, sid, force_refresh=True)
        except:
            pass

if __name__ == "__main__":
    main()
