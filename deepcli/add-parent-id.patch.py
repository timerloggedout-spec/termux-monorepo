import re

with open('deepcli.py', 'r') as f:
    content = f.read()

# Add --parent-id argument to send parser
old_send_parser = '''    p_send = sub.add_parser("send", help="Send a message")
    p_send.add_argument("prompt", help="Your message")
    p_send.add_argument("--session", help="Session ID (default: last used)")
    p_send.add_argument("--attach", nargs="+", help="File(s) to attach")
    p_send.add_argument("--thinking", action="store_true", default=None)
    p_send.add_argument("--search", action="store_true", default=None)'''
new_send_parser = '''    p_send = sub.add_parser("send", help="Send a message")
    p_send.add_argument("prompt", help="Your message")
    p_send.add_argument("--session", help="Session ID (default: last used)")
    p_send.add_argument("--parent-id", help="Parent message ID (assistant message to continue from)")
    p_send.add_argument("--attach", nargs="+", help="File(s) to attach")
    p_send.add_argument("--thinking", action="store_true", default=None)
    p_send.add_argument("--search", action="store_true", default=None)'''
content = content.replace(old_send_parser, new_send_parser)

# Update cmd_send to use args.parent_id if provided
old_cmd_send_parent = '''    # Get parent message ID from history if available
    try:
        msgs = get_history(token, sid)
        if msgs:
            parent_id = msgs[-1].get("message_id")
        else:
            parent_id = None
    except Exception:
        parent_id = None'''

new_cmd_send_parent = '''    # Get parent message ID: use --parent-id if given, else infer from history
    if args.parent_id:
        parent_id = args.parent_id
    else:
        try:
            msgs = get_history(token, sid)
            if msgs:
                parent_id = msgs[-1].get("message_id")
            else:
                parent_id = None
        except Exception:
            parent_id = None'''

content = content.replace(old_cmd_send_parent, new_cmd_send_parent)

with open('deepcli.py', 'w') as f:
    f.write(content)
print("✅ Added --parent-id to send")
