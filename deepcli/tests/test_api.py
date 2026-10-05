"""Opt-in live DeepSeek API integration tests (network-gated).

This module is SKIPPED unless the environment variable ``DEEPCLI_API_TESTS``
is set to ``1``. By default the standard suite therefore stays offline and
deterministic; CI never makes outbound calls unless it explicitly opts in.

Every test here performs real network I/O and creates real server-side chat
sessions, so treat it as an integration smoke test, not a unit test.

Import bootstrap: sys.path is rooted at *this checkout* (derived from
``__file__``), not at ``$HOME/deepcli``, so a git worktree exercises the
worktree's own code.
"""

import os
import sys
import time
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT))

from deepcli import (
    get_token,
    get_session,
    upload_file,
    wait_for_file,
    branch_conversation,
    stream_completion,
    create_session,
    fetch_sessions,
    get_history,
)

BASE = "https://chat.deepseek.com/api/v0"
OPT_IN = os.environ.get("DEEPCLI_API_TESTS") == "1"


@unittest.skipUnless(
    OPT_IN,
    "live network tests; set DEEPCLI_API_TESTS=1 to enable",
)
class TestDeepSeekAPI(unittest.TestCase):
    """Live DeepSeek API integration tests (opt-in only)."""

    def test_auth(self):
        token = get_token()
        s = get_session(token)
        r = s.get(f"{BASE}/users/current")
        self.assertEqual(r.status_code, 200)
        self.assertIn("biz_data", r.json().get("data", {}))

    def test_create_session(self):
        token = get_token()
        sid = create_session(token)
        self.assertTrue(sid, f"no session id returned: {sid!r}")

    def test_upload(self):
        token = get_token()
        test_file = Path.home() / "test.txt"
        if not test_file.exists():
            test_file.write_text("Hello DeepSeek test upload!")
        fid = upload_file(token, "test", str(test_file))
        self.assertTrue(fid, "no file_id returned")
        self.assertTrue(wait_for_file(token, fid, timeout=30))

    def test_branch(self):
        token = get_token()
        sid = create_session(token)
        try:
            stream_completion(token, "Branch test", sid, auto_retry=False)
        except Exception:
            pass
        time.sleep(1)
        messages = get_history(token, sid)
        assistants = [m for m in messages if m.get("role", "").upper() == "ASSISTANT"]
        self.assertTrue(assistants, "no assistant messages to branch from")
        target_id = assistants[-1]["message_id"]
        new_sid = branch_conversation(token, sid, target_id)
        self.assertIsNotNone(new_sid)
        self.assertNotEqual(new_sid, sid)

    def test_list_sessions(self):
        token = get_token()
        sessions = fetch_sessions(token)
        self.assertGreater(len(sessions), 0)

    def test_stream(self):
        token = get_token()
        sid = create_session(token)
        # Raises on failure; reaching here means the stream completed.
        stream_completion(token, "Say hello in one word", sid, auto_retry=False)


if __name__ == "__main__":
    unittest.main()
