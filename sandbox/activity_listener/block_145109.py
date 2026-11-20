\")
    except: pass"""
new_chat = """def send_chat(text):
    \"\"\"Send output back to this chat via stream_completion (TUI method).\"\"\"
    try:
        sys.path.insert(0, str(HOME / 'deepcli'))
        from deepcli.core import get_token, stream_completion
        stream_completion(get_token(), f\"🤖 [Auto‑Exec]\\n