#!/usr/bin/env python3
"""Export code blocks from ALL accessible DeepSeek conversations."""
import sys, json, re, hashlib
from pathlib import Path

HOME = Path.home()
DOWNLOADS = HOME / 'storage' / 'downloads' / 'synthegration_batch_export'

sys.path.insert(0, str(HOME / 'deepcli'))
from deepcli.core import get_token, fetch_sessions, get_history
sys.path.insert(0, str(HOME / 'cli-synthegration'))
from synthegration_index import CodexIndex, Pointer

def export_session(token, session):
    sid = session['id']
    title = session.get('title', 'Untitled')
    safe_title = re.sub(r'[\\/*?:"<>|\[\]]', '_', title)[:60]
    out_dir = DOWNLOADS / safe_title
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        msgs = get_history(token, sid)
        blocks = []
        for msg in msgs:
            content = msg.get('content', '')
            for match in re.finditer(r"```(\w+)?\n(.*?)```", content, re.DOTALL):
                lang = (match.group(1) or 'text').lower()
                code = match.group(2)
                h = hashlib.sha256(code.encode()).hexdigest()[:8]
                ext = {"python":"py","javascript":"js","typescript":"ts","bash":"sh","html":"html","css":"css","json":"json"}.get(lang, lang)
                fname = f"{lang}_{h}.{ext}"
                (out_dir / fname).write_text(code)
                blocks.append({
                    "conversation_id": sid,
                    "conversation_title": title,
                    "language": lang,
                    "code_hash": h,
                    "file": fname
                })
        if blocks:
            (out_dir / 'manifest.json').write_text(json.dumps(blocks, indent=2))
            print(f"  {safe_title}: {len(blocks)} blocks")
        return len(blocks)
    except Exception as e:
        print(f"  {safe_title}: ERROR - {e}")
        return 0

def main():
    token = get_token()
    sessions = fetch_sessions(token)
    print(f"Exporting {len(sessions)} sessions to {DOWNLOADS}...")
    total_blocks = 0
    for i, s in enumerate(sessions):
        sys.stdout.write(f"[{i+1}/{len(sessions)}] ")
        sys.stdout.flush()
        total_blocks += export_session(token, s)
    print(f"\nDone. Total blocks exported: {total_blocks}")

if __name__ == "__main__":
    main()
