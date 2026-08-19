from __future__ import annotations

import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import sys
from pathlib import Path

original_path = sys.path.copy()
deepcli_dir = str(Path(__file__).resolve().parent.parent / "deepcli")
while deepcli_dir in sys.path:
    sys.path.remove(deepcli_dir)

try:
    from deepcli import session_manager
finally:
    sys.path = original_path


class DeepSeekWafSessionTests(unittest.TestCase):
    def test_cookie_export_preserves_waf_and_session_cookies(self):
        exported = json.dumps(
            [
                {"name": "ds_session_id", "value": "session-value"},
                {"name": "aws-waf-token", "value": "waf-value"},
                {"name": "ds_cookie_preference", "value": "preference-value"},
            ]
        )
        jar = session_manager._extract_cookie_jar(exported)
        self.assertEqual(
            jar,
            {
                "ds_session_id": "session-value",
                "aws-waf-token": "waf-value",
                "ds_cookie_preference": "preference-value",
            },
        )

    def test_cookie_map_rejects_metadata_and_trims_values(self):
        jar = session_manager._extract_cookie_jar(
            json.dumps(
                {
                    "cookies": {
                        "ds_session_id": " session-value ",
                        "aws-waf-token": " waf-value ",
                        "metadata": {"ignored": True},
                        "bad cookie name": "ignored",
                    }
                }
            )
        )
        self.assertEqual(
            jar,
            {"ds_session_id": "session-value", "aws-waf-token": "waf-value"},
        )

    def test_explicit_waf_env_extends_imported_cookie_jar(self):
        exported = json.dumps(
            {"cookies": [{"name": "ds_session_id", "value": "session-value"}]}
        )
        with patch.dict(
            os.environ,
            {
                "DEEPSEEK_COOKIES": exported,
                "DEEPSEEK_AWS_WAF_TOKEN": "waf-value",
            },
            clear=True,
        ):
            jar = session_manager._cookie_jar_from_env("primary")
        self.assertEqual(jar["ds_session_id"], "session-value")
        self.assertEqual(jar["aws-waf-token"], "waf-value")

    def test_new_session_carries_full_cookie_jar_without_cookies_file(self):
        exported = json.dumps(
            [
                {"name": "ds_session_id", "value": "session-value"},
                {"name": "aws-waf-token", "value": "waf-value"},
            ]
        )
        with patch.dict(
            os.environ,
            {"DEEPSEEK_TOKEN": "bearer-value", "DEEPSEEK_COOKIES": exported},
            clear=True,
        ), patch.object(session_manager, "create_chat_session", return_value="chat-id") as create:
            session = session_manager.get_new_session("primary")
        self.assertEqual(session["cookies"]["ds_session_id"], "session-value")
        self.assertEqual(session["cookies"]["aws-waf-token"], "waf-value")
        create.assert_called_once_with(
            "bearer-value",
            cookies={"ds_session_id": "session-value", "aws-waf-token": "waf-value"},
            model_type="expert",
        )

    def test_resumed_session_refreshes_waf_cookie_and_persists_it(self):
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict(
            os.environ,
            {
                "DEEPSEEK_AWS_WAF_TOKEN": "new-waf-value",
                "DEEPSEEK_WAF_TOKEN_REFRESH": "1",
            },
            clear=True,
        ):
            cache_path = Path(temp_dir) / "primary" / "session.json"
            cache_path.parent.mkdir(mode=0o700)
            cache_path.write_text(
                json.dumps(
                    {
                        "account": "primary",
                        "token": "bearer-value",
                        "cookies": {"ds_session_id": "session-value", "aws-waf-token": "old-waf-value"},
                        "chat_session_id": "chat-id",
                        "expires": time.time() + 3600,
                    }
                ),
                encoding="utf-8",
            )
            session = session_manager.ensure_session(temp_dir, "primary")
            persisted = json.loads(cache_path.read_text(encoding="utf-8"))
        self.assertEqual(session["cookies"]["aws-waf-token"], "new-waf-value")
        self.assertEqual(persisted["cookies"]["aws-waf-token"], "new-waf-value")

    def test_workflow_cache_is_repo_and_ref_scoped_without_restore_prefix(self):
        workflow = (Path(__file__).parent.parent / ".github/workflows/deepseek-ci.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("github.repository_id", workflow)
        self.assertIn("github.ref", workflow)
        self.assertNotIn("restore-keys:", workflow)

    def test_resumed_session_keeps_cached_waf_without_refresh_flag(self):
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict(
            os.environ,
            {"DEEPSEEK_AWS_WAF_TOKEN": "new-waf-value"},
            clear=True,
        ):
            cache_path = Path(temp_dir) / "primary" / "session.json"
            cache_path.parent.mkdir(mode=0o700)
            cache_path.write_text(
                json.dumps(
                    {
                        "account": "primary",
                        "token": "bearer-value",
                        "cookies": {"ds_session_id": "session-value", "aws-waf-token": "cached-waf-value"},
                        "chat_session_id": "chat-id",
                        "expires": time.time() + 3600,
                    }
                ),
                encoding="utf-8",
            )
            session = session_manager.ensure_session(temp_dir, "primary")
            persisted = json.loads(cache_path.read_text(encoding="utf-8"))
        self.assertEqual(session["cookies"]["aws-waf-token"], "cached-waf-value")
        self.assertEqual(persisted["cookies"]["aws-waf-token"], "cached-waf-value")

    def test_ensure_session_rejects_symlink_cache_file(self):
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict(
            os.environ,
            {"DEEPSEEK_TOKEN": "test-token"},
            clear=True,
        ):
            target_file = Path(temp_dir) / "sensitive.txt"
            target_file.write_text("sensitive-data", encoding="utf-8")
            if os.name != "nt":
                target_file.chmod(0o644)

            primary_dir = Path(temp_dir) / "primary"
            primary_dir.mkdir(parents=True, exist_ok=True)
            cache_path = primary_dir / "session.json"
            cache_path.symlink_to(target_file)

            with self.assertRaises(ValueError):
                session_manager.ensure_session(temp_dir, "primary")

            # Verify target content & mode were uncorrupted
            self.assertEqual(target_file.read_text(encoding="utf-8"), "sensitive-data")
            if os.name != "nt":
                self.assertEqual(target_file.stat().st_mode & 0o777, 0o644)


if __name__ == "__main__":
    unittest.main()
