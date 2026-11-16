TUI = '/data/data/com.termux/files/home/deepcli-tui/tui.py'
with open(TUI) as f:
    content = f.read()

# Add /back command before /help check
old = "if user_input.lower() == '/help':"
new = """if user_input.lower() == '/back':
            # Return to session selection
            sid, model_mode = prompt_session_id()
            if sid == 'new':
                sid = create_session(token)
                console.print(f"Created session: {sid}")
            parent_id = None
            show_full_tree = False
            console.clear()
            continue
        if user_input.lower() == '/help':"""
content = content.replace(old, new)

with open(TUI, 'w') as f:
    f.write(content)
print("✅ TUI: /back command added.")
