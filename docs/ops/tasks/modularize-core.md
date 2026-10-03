# REVIEW REQUIRED — produce PLAN.md first

Before any edit, produce PLAN.md in the worktree enumerating:

1. Which line ranges of deepcli/deepcli/core.py move to which module
2. Which names stay in core.py (public surface)
3. Every import core.py needs after the split
4. Cycle risks and how they are broken
5. Verification checklist

Then finish with the PLAN. Do NOT proceed to edits until reviewed.

---

# Task: modularize deepcli/deepcli/core.py

## Target

588 lines, single file. Split into focused modules alongside the
already-shipped _v1_cache.py, _v1_events.py, _v1_preflight.py.

## Proposed split

| New module        | Contents |
|-------------------|----------|
| _v1_session.py    | get_token, create_session, get_session, fetch_sessions |
| _v1_history.py    | get_history, _cache_path, _cache_load, _cache_save |
| _v1_pow.py        | get_pow_challenge, solve_pow |
| _v1_stream.py     | stream_completion, chat_completion, continue_response |
| _v1_upload.py     | upload_file, wait_for_file |
| _v1_feedback.py   | submit_feedback, get_last_assistant_message_id |
| _v1_export.py     | export_markdown, export_json |
| _v1_branch.py     | branch_conversation |

## Public surface (must stay importable from deepcli.core)

get_token, create_session, get_session, fetch_sessions,
get_history, get_pow_challenge, solve_pow,
stream_completion, chat_completion, continue_response,
upload_file, wait_for_file, branch_conversation,
submit_feedback, get_last_assistant_message_id,
export_markdown, export_json,
_cache_path, _cache_load, _cache_save,
BASE_URL, CONFIG_FILE, CONFIG_DIR

## Invariant

core.py becomes a thin re-export shim. Every existing call site keeps
working. No behavioral change. No new dependencies. All 20 tests pass.

## Verify

- python3 deepcli/tests/run.py  ->  20/20
- python3 -c "from deepcli.core import get_token, stream_completion, get_history; print('ok')"
- one live chat_completion returns the correct phrase
