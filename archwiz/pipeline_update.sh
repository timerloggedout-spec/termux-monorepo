#!/bin/bash
set -e
HOME_DIR="$HOME"
EXPORT_DIR="$HOME_DIR/synthegration_exports"
SESSION_STORE="$HOME_DIR/.deepcli/session_store"
LAST_RUN="$HOME_DIR/.deepcli/.pipeline_last_run"

echo "[1/5] Fetching all session histories from API..."
python3 -c "
import sys, json
from pathlib import Path
HOME = Path.home()
sys.path.insert(0, str(HOME / 'deepcli'))
from deepcli.core import get_token, fetch_sessions, get_history
EXPORT_DIR = HOME / 'synthegration_exports'
EXPORT_DIR.mkdir(parents=True, exist_ok=True)
token = get_token()
sessions = fetch_sessions(token)
total_blocks = exported = 0
for s in sessions:
    sid = s.get('id',''); title = s.get('title','untitled')
    if not sid: continue
    out = EXPORT_DIR / sid; out.mkdir(exist_ok=True)
    if (out / 'session.json').exists() and (out / 'session.json').stat().st_size > 100:
        continue
    try:
        history = get_history(token, sid, force_refresh=False)
        (out / 'session.json').write_text(json.dumps(history, indent=2))
        blocks = sum(m.get('content','').count('\`\`\`')//2 for m in history if isinstance(m,dict) and m.get('role')=='ASSISTANT')
        total_blocks += blocks; exported += 1
        print(f'  {blocks} blocks → {sid[:8]} ({title[:60]})')
    except Exception as e:
        print(f'  skip {sid[:8]}: {e}')
print(f'Done: {total_blocks} blocks from {exported} new sessions')
"

echo "[2/5] Syncing to session store..."
mkdir -p "$SESSION_STORE"
new=0
for dir in "$EXPORT_DIR"/*/; do
    [ -d "$dir" ] || continue
    sid=$(basename "$dir")
    for jf in "$dir"/session.json "$dir"/*.json; do
        [ -f "$jf" ] || continue
        [[ "$jf" == *manifest.json ]] && continue
        dest="$SESSION_STORE/${sid}.json"
        [ "$jf" -nt "$dest" ] 2>/dev/null && cp "$jf" "$dest" && ((new++)) || true
        break
    done
done
echo "   $new new/updated in store"

echo "[3/5] Session digest..."
python3 -c "
import sys, pathlib
sys.path.insert(0, '$HOME_DIR/archwiz')
import session_digest
session_digest.HOME = pathlib.Path('$HOME_DIR')
session_digest.EXPORTS_DIR = session_digest.HOME / 'synthegration_exports'
session_digest.generate(session_digest.scan())
"

echo "[4/5] Pointer index..."
python3 -c "
import json, hashlib, re
from pathlib import Path
HOME = Path('$HOME_DIR')
EXPORTS = HOME / 'synthegration_exports'
INDEX = HOME / 'archwiz' / 'pointer_index.json'
FENCE = re.compile(r'\`\`\`(\w*)\n(.*?)\`\`\`', re.DOTALL)
idx = {}
for d in EXPORTS.iterdir():
    if not d.is_dir(): continue
    for f in d.glob('session.json'):
        try:
            msgs = json.loads(f.read_text())
            if not isinstance(msgs, list): continue
        except: continue
        for mi, m in enumerate(msgs):
            if not isinstance(m, dict): continue
            for blk_i, match in enumerate(FENCE.finditer(m.get('content',''))):
                h = hashlib.sha256(match.group(2).encode()).hexdigest()[:16]
                idx[h] = {'session_id': d.name, 'message_idx': mi, 'block_idx': blk_i}
INDEX.write_text(json.dumps(idx, indent=2))
print(f'Pointer index: {len(idx)} code blocks')
"

echo "[5/5] Lexicon harvest..."
python3 "$HOME_DIR/archwiz/lexicon_harvest.py" scan 100 2>/dev/null || echo "   (lexicon scan skipped)"

date +%s > "$LAST_RUN"
echo "✅ Pipeline complete. $(date)"
