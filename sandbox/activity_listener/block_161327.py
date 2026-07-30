",
                         send_sid, None, thinking=False, search=False)
    except: pass'''
new_chat = '''def send_chat(text):
    """Send output back to this chat via stream_completion."""
    try:
        sys.path.insert(0, str(HOME / 'deepcli'))
        from deepcli.core import get_token, stream_completion
        # Call exactly like the TUI – no capture
        stream_completion(get_token(), f"🤖 [Auto‑Exec]\\n