# 🪄 Utility Belt – Reusable CLI Spells
Each spell is a standalone Python script that uses token_provider_v2 for auth.

| Spell | Purpose | Example |
|-------|---------|---------|
| `verify-session.py` | Confirm a session belongs to an account | `python3 verify-session.py primary <uuid>` |
| `fetch-session.py` | Print message history for a session | `python3 fetch-session.py secondary <uuid>` |
| `list-sessions.py` | List recent chat sessions | `python3 list-sessions.py secondary` |
| `extract_token_bookmarklet.py` | Extract Bearer token from cookies | (from `harmony_hub/src/`) |
| `direct_task.py` | Run agent refactor on any file | (from `harmony_hub/workspace/agent/`) |
| `promote.py` | Safely promote sandbox → production | (from `harmony_hub/workspace/agent/`) |
| `fts_search.sh` | Full‑text search conversations | `fts_search '🌿'` |
