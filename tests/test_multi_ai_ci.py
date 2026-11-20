import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "multi-ai-cli"))

from ci_mode import main, run_ci


def test_run_ci_offline_mock(monkeypatch):
    temp_dir = tempfile.mkdtemp()
    try:
        import backends.deepseek as ds_mod
        import subprocess

        monkeypatch.setenv("DEEPSEEK_TOKEN", "test-model-token")
        monkeypatch.setattr(
            ds_mod.DeepSeekBackend,
            "send_message",
            lambda self, msg, context: "Mocked Code Review: LGTM!",
        )
        monkeypatch.setattr(
            ds_mod.DeepSeekBackend,
            "__init__",
            lambda self, session_manager: None,
        )
        monkeypatch.setattr(
            subprocess,
            "check_output",
            lambda *a, **k: "diff --git a/x b/x\n+hello",
        )
        monkeypatch.setattr(
            subprocess,
            "run",
            lambda *a, **k: type("R", (), {"returncode": 0})(),
        )

        event_data = {
            "action": "synchronize",
            "pull_request": {"number": 137},
            "repository": {"full_name": "test/repo"},
        }
        result = run_ci(
            event=event_data,
            workspace=temp_dir,
            operator_token="test_token",
        )

        assert result is not None
        assert result["provider_used"] == "deepseek"
        assert result["status"] == "ok"
        assert len(result["actions"]) == 1
        assert result["actions"][0]["type"] == "pr_review"
        assert result["actions"][0].get("posted") is True
    finally:
        shutil.rmtree(temp_dir)


def test_ci_output_permissions(monkeypatch):
    temp_dir = tempfile.mkdtemp()
    try:
        cache_dir = Path(temp_dir) / "cache"
        event_path = Path(temp_dir) / "event.json"
        event_data = {
            "action": "opened",
            "pull_request": {"number": 137},
            "repository": {"full_name": "test/repo"},
        }
        with open(event_path, "w", encoding="utf-8") as f:
            json.dump(event_data, f)

        monkeypatch.setenv("GITHUB_EVENT_PATH", str(event_path))
        monkeypatch.setenv("OPERATOR_TOKEN", "test_token")
        monkeypatch.setenv("DEEPSEEK_TOKEN", "test-model-token")

        import backends.deepseek as ds_mod
        import subprocess

        monkeypatch.setattr(
            ds_mod.DeepSeekBackend,
            "__init__",
            lambda self, session_manager: None,
        )
        monkeypatch.setattr(
            ds_mod.DeepSeekBackend,
            "send_message",
            lambda self, msg, ctx: "Mocked output!",
        )
        monkeypatch.setattr(
            subprocess,
            "check_output",
            lambda *a, **k: "diff",
        )
        monkeypatch.setattr(
            subprocess,
            "run",
            lambda *a, **k: type("R", (), {"returncode": 0})(),
        )
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "ci_mode.py",
                "--workspace",
                temp_dir,
                "--cache-dir",
                str(cache_dir),
            ],
        )

        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        try:
            main()
            assert cache_dir.exists()
            assert (os.stat(cache_dir).st_mode & 0o777) == 0o700
            output_file = Path("deepseek_output.json")
            assert output_file.exists()
            assert (os.stat(output_file).st_mode & 0o777) == 0o600
            data = json.loads(output_file.read_text(encoding="utf-8"))
            # Metadata only — no model body
            assert "Mocked" not in json.dumps(data)
            assert data.get("status") == "ok"
        finally:
            os.chdir(original_cwd)
    finally:
        shutil.rmtree(temp_dir)
