#!/usr/bin/env python3
"""Additive post-ingestion dispatch. Called after session cache writes.
Non-blocking: failures are logged to stderr and never raise to the caller."""
import json
import sys
from pathlib import Path
from typing import Optional, List

HOME = Path.home()


def _resolve_session_store(
    session_id: str,
    account: str = "primary",
    provider: Optional[str] = None,
    store_path: Optional[str] = None,
) -> Optional[Path]:
    """Find session JSON across known provider store roots.

    Order:
      1. explicit store_path
      2. provider-specific roots (mistral, deepseek)
      3. deepcli account + flat fallbacks
      4. multi-ai-cache flat session id
    """
    candidates: List[Path] = []

    if store_path:
        candidates.append(Path(store_path).expanduser())

    prov = (provider or "").lower().strip()
    if prov in ("mistral", "mistralai", ""):
        candidates.append(HOME / ".mistralai-cli" / "session_store" / account / f"{session_id}.json")
        candidates.append(HOME / ".mistralai-cli" / "session_store" / f"{session_id}.json")

    if prov in ("deepseek", "deepcli", ""):
        candidates.append(HOME / ".deepcli" / "session_store" / account / f"{session_id}.json")
        candidates.append(HOME / ".deepcli" / "session_store" / f"{session_id}.json")

    # Always allow cross-provider discovery when provider omitted or unknown
    if prov not in ("mistral", "mistralai", "deepseek", "deepcli"):
        candidates.append(HOME / ".mistralai-cli" / "session_store" / account / f"{session_id}.json")
        candidates.append(HOME / ".mistralai-cli" / "session_store" / f"{session_id}.json")
        candidates.append(HOME / ".deepcli" / "session_store" / account / f"{session_id}.json")
        candidates.append(HOME / ".deepcli" / "session_store" / f"{session_id}.json")

    candidates.append(HOME / ".multi-ai-cache" / f"{session_id}.json")

    seen = set()
    for path in candidates:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        if path.is_file():
            return path
    return None


def update_all(
    session_id: str,
    account: str = "primary",
    provider: Optional[str] = None,
    store_path: Optional[str] = None,
):
    """Run downstream updates for a session. Lightweight — no subprocess calls."""
    store = _resolve_session_store(session_id, account=account, provider=provider, store_path=store_path)
    if store is None:
        print(
            f"[archwiz dispatch] no session store for id={session_id!r} "
            f"account={account!r} provider={provider!r}",
            file=sys.stderr,
            flush=True,
        )
        return

    try:
        with open(store) as f:
            msgs = json.load(f)
    except Exception as e:
        print(
            f"[archwiz dispatch] load {store}: {type(e).__name__}: {e}",
            file=sys.stderr,
            flush=True,
        )
        return

    # Normalize list vs wrapper objects
    if isinstance(msgs, dict) and "messages" in msgs:
        msgs = msgs["messages"]
    if not isinstance(msgs, list):
        print(
            f"[archwiz dispatch] unexpected session shape at {store}: {type(msgs).__name__}",
            file=sys.stderr,
            flush=True,
        )
        return

    # 1. Write session.json into export dir (namespaced by account; optional provider subdir)
    export_root = HOME / "synthegration_exports" / account
    if provider:
        export_root = export_root / provider
    export_dir = export_root / session_id
    export_dir.mkdir(parents=True, exist_ok=True)
    (export_dir / "session.json").write_text(json.dumps(msgs, indent=2))

    # 2. Lexicon harvest (lightweight: single session)
    try:
        sys.path.insert(0, str(HOME / "archwiz"))
        from lexicon_harvest import harvest_session

        harvest_session(session_id)
    except Exception as e:
        print(f"[archwiz dispatch] lexicon_harvest: {type(e).__name__}: {e}", file=sys.stderr, flush=True)

    # 3. Codex index (incremental add — does NOT rebuild full index)
    try:
        sys.path.insert(0, str(HOME / "cli-synthegration"))
        from synthegration_index import CodexIndex

        codex = CodexIndex(HOME / "cli-synthegration" / "codex")
        codex.index_conversation(session_id, session_id[:8], msgs)
        codex._save()
    except Exception as e:
        print(f"[archwiz dispatch] codex_index: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
