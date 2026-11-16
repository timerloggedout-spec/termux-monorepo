# This Python script patches deepcli.py to add --ids to history command
import re

with open('deepcli.py', 'r') as f:
    content = f.read()

# Add --ids argument to the history subparser
old_hist_parser = '''    p_hist = sub.add_parser("history", help="Show conversation history")
    p_hist.add_argument("--session", help="Session ID")'''
new_hist_parser = '''    p_hist = sub.add_parser("history", help="Show conversation history")
    p_hist.add_argument("--session", help="Session ID")
    p_hist.add_argument("--ids", action="store_true", help="Show message IDs and parent IDs")'''
content = content.replace(old_hist_parser, new_hist_parser)

# Update cmd_history function to use args.ids
old_cmd_history = '''def cmd_history(args):
    token = get_token()
    sid = args.session or load_config().get("last_session")
    if not sid:
        console.print("[red]No session specified.[/]")
        return
    messages = get_history(token, sid)
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "user":
            console.print(f"[blue]You:[/] {content}")
        else:
            console.print(f"[green]DeepSeek:[/] {content}")
        console.print("-" * 40)'''

new_cmd_history = '''def cmd_history(args):
    token = get_token()
    sid = args.session or load_config().get("last_session")
    if not sid:
        console.print("[red]No session specified.[/]")
        return
    messages = get_history(token, sid)
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        mid = msg.get("message_id")
        pid = msg.get("parent_id")
        if role == "user":
            line = f"[blue]You (ID:{mid}, parent:{pid}):[/] {content}"
        else:
            line = f"[green]DeepSeek (ID:{mid}, parent:{pid}):[/] {content}"
        if args.ids:
            console.print(line)
        else:
            if role == "user":
                console.print(f"[blue]You:[/] {content}")
            else:
                console.print(f"[green]DeepSeek:[/] {content}")
        console.print("-" * 40)'''

content = content.replace(old_cmd_history, new_cmd_history)

with open('deepcli.py', 'w') as f:
    f.write(content)
print("✅ Added --ids to history")
