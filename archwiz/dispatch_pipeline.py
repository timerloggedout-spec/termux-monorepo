#!/usr/bin/env python3
"""Additive post‑ingestion dispatch. Called by core.py after every session fetch.
Non‑blocking: all heavy operations run via background scripts."""
import json
import sys
from pathlib import Path

HOME = Path.home()

def update_all(session_id: str, account: str = "primary"):
    """Run downstream updates for a session. Lightweight — no subprocess calls."""
    store = HOME / '.deepcli' / 'session_store' / account / f'{session_id}.json'
    # Fallback to flat store if not in account subdir
    if not store.exists():
        store = HOME / '.deepcli' / 'session_store' / f'{session_id}.json'
    if not store.exists():
        return

    try:
        with open(store) as f:
            msgs = json.load(f)
    except Exception as e:
        print(f"[archwiz dispatch] load session {session_id}: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
        return

    # 1. Write session.json into export dir
    export_dir = HOME / 'synthegration_exports' / account / session_id
    export_dir.mkdir(parents=True, exist_ok=True)
    (export_dir / 'session.json').write_text(json.dumps(msgs, indent=2))

    # 2. Lexicon harvest (lightweight: single session)
    try:
        sys.path.insert(0, str(HOME / 'archwiz'))
        from lexicon_harvest import harvest_session
        harvest_session(session_id)
    except Exception as e:
        print(f"[archwiz dispatch] lexicon_harvest: {type(e).__name__}: {e}", file=sys.stderr, flush=True)

    # 3. Codex index (incremental add — does NOT rebuild full index)
    try:
        sys.path.insert(0, str(HOME / 'cli-synthegration'))
        from synthegration_index import CodexIndex
        codex = CodexIndex(HOME / 'cli-synthegration' / 'codex')
        codex.index_conversation(session_id, session_id[:8], msgs)
        codex._save()
    except Exception as e:
        print(f"[archwiz dispatch] codex_index: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
