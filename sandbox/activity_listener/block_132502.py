", SESSION_ID, None)
    except: pass

# Track executed blocks by msg_id + code hash
executed = set()
if EXECUTED.exists():
    executed = set(l.strip() for l in EXECUTED.read_text().splitlines() if l.strip())

last_msg_id = None
while True:
    try:
        msgs = fetch()
        if not msgs: time.sleep(15); continue
        cur = str(msgs[-1].get('message_id', ''))
        if cur == last_msg_id: time.sleep(5); continue
        last_msg_id = cur

        for m in reversed(msgs):
            if m.get('role', '').lower() != 'assistant': continue
            mid = str(m.get('message_id', ''))
            content = m.get('content', '')
            for match in re.finditer(r'