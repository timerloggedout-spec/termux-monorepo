#!/usr/bin/env python3
"""Incremental sync: only fetch sessions updated after baseline, reuse deepcli message cache."""
import sys, json, hashlib, re, os
from pathlib import Path

HOME = Path.home()
EXPORTS = HOME / 'synthegration_exports'
EXPORTS.mkdir(parents=True, exist_ok=True)
CACHE_FILE = HOME / '.cache' / 'synthegration' / 'sync_state.json'
BASELINE_FILE = HOME / 'cli-synthegration' / 'sync' / 'baseline.json'
CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

sync_state = json.loads(CACHE_FILE.read_text()) if CACHE_FILE.exists() else {}
baseline = json.loads(BASELINE_FILE.read_text()).get('baseline', 0) if BASELINE_FILE.exists() else 0
print(f"Baseline: {baseline}  |  Already synced: {len(sync_state)}", file=sys.stderr)

sys.path.insert(0, str(HOME / 'deepcli'))
from deepcli.core import get_token, fetch_sessions, get_history

token = get_token()
sessions = fetch_sessions(token)
print(f"Server sessions: {len(sessions)}", file=sys.stderr)

new = updated = skipped = 0
for idx, s in enumerate(sessions, 1):
    sid = s['id']
    server_ts = s.get('updated_at', 0)

    # Skip sessions already up‑to‑date
    if str(server_ts) <= str(sync_state.get(sid, baseline)):
        skipped += 1
        continue

    print(f"[{idx}/{len(sessions)}] {s.get('title','')[:60]}", file=sys.stderr, flush=True)

    try:
        msgs = get_history(token, sid)  # uses deepcli cache automatically
    except Exception as e:
        print(f"  SKIP: {e}", file=sys.stderr)
        continue

    title = re.sub(r'[\\/*?:"<>|\[\]\n\r]', '_', s.get('title', 'Untitled'))[:60]
    out = EXPORTS / f"{title}_{sid[:8]}"
    out.mkdir(parents=True, exist_ok=True)

    blocks = []
    for msg in msgs:
        content = msg.get('content', '')
        thinking = msg.get('thinking_content', '')
        if thinking and thinking != 'None':
            (out / f"thinking_{msg.get('message_id','0')}.md").write_text(thinking)
            blocks.append({'msg_id': msg.get('message_id'), 'role': msg.get('role'),
                           'language': 'thinking', 'code_snippet': thinking[:200]})
        for match in re.finditer(r"```(\w*)\n(.*?)```", content, re.DOTALL):
            lang = (match.group(1) or 'text').strip()[:20]
            code = match.group(2)
            h = hashlib.sha256(code.encode()).hexdigest()[:12]
            ext = {'python': 'py', 'javascript': 'js', 'typescript': 'ts', 'bash': 'sh',
                   'rust': 'rs', 'html': 'html', 'css': 'css', 'json': 'json',
                   'yaml': 'yaml', 'markdown': 'md'}.get(lang, lang)
            (out / f"{lang}_{h}.{ext}").write_text(code)
            blocks.append({'msg_id': msg.get('message_id'), 'role': msg.get('role'),
                           'language': lang, 'code_hash': h, 'code_snippet': code[:200]})

    (out / 'manifest.json').write_text(json.dumps(blocks, indent=2))
    (out / 'messages.json').write_text(json.dumps(msgs, indent=2, ensure_ascii=False))
    sync_state[sid] = server_ts
    if str(sync_state.get(sid, '0')) == '0':
        new += 1
    else:
        updated += 1

CACHE_FILE.write_text(json.dumps(sync_state, indent=2))
print(f"\nDone: {new} new, {updated} updated, {skipped} unchanged", file=sys.stderr)
