",
                         SESSION_ID, None, thinking=False, search=False)
    except: pass'''
new2 = '''def send_chat(text):
    """Send output back to this chat via deepapi.py."""
    try:
        subprocess.run(['python3', str(HOME/'archwiz/send_helper.py'),
                        f"🤖 [Auto‑Exec]\\n