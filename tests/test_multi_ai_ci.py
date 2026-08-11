import os
import json
import tempfile
import shutil
import pytest
from pathlib import Path

# Add multi-ai-cli directory to python path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "multi-ai-cli"))

from ci_mode import run_ci, main

def test_run_ci_permissions():
    # Create secure temporary directory
    temp_dir = tempfile.mkdtemp()
    try:
        # We will mock the DeepSeekBackend send_message to return a mock string
        # so that it executes completely offline without network requirements
        import backends.deepseek as ds_mod
        original_send = ds_mod.DeepSeekBackend.send_message
        ds_mod.DeepSeekBackend.send_message = lambda self, msg, context: "Mocked Code Review: LGTM!"

        # Mock os.environ to contain GITHUB_EVENT_PATH
        event_path = Path(temp_dir) / 'event.json'
        event_data = {
            'action': 'synchronize',
            'pull_request': {'number': 137},
            'repository': {'full_name': 'test/repo'}
        }
        with open(event_path, 'w') as f:
            json.dump(event_data, f)

        os.environ['GITHUB_EVENT_PATH'] = str(event_path)
        os.environ['OPERATOR_TOKEN'] = 'test_token'

        # Call run_ci
        result = run_ci(
            event=event_data,
            workspace=temp_dir,
            operator_token='test_token'
        )

        assert result is not None
        assert result['provider_used'] == 'deepseek'
        assert result['event'] == 'synchronize'
        assert len(result['actions']) == 1
        assert "Mocked Code Review" in result['actions'][0]['summary']

        # Restore original function
        ds_mod.DeepSeekBackend.send_message = original_send

    finally:
        shutil.rmtree(temp_dir)

def test_ci_output_permissions(monkeypatch):
    # Mock ci_mode main execution
    temp_dir = tempfile.mkdtemp()
    try:
        cache_dir = Path(temp_dir) / 'cache'
        event_path = Path(temp_dir) / 'event.json'
        event_data = {
            'action': 'opened',
            'pull_request': {'number': 137},
            'repository': {'full_name': 'test/repo'}
        }
        with open(event_path, 'w') as f:
            json.dump(event_data, f)

        monkeypatch.setenv('GITHUB_EVENT_PATH', str(event_path))
        monkeypatch.setenv('OPERATOR_TOKEN', 'test_token')

        import backends.deepseek as ds_mod
        monkeypatch.setattr(
            ds_mod.DeepSeekBackend,
            "send_message",
            lambda self, msg, ctx: "Mocked output!"
        )

        # Execute main with argparse arguments
        monkeypatch.setattr(sys, "argv", [
            "ci_mode.py",
            "--workspace", temp_dir,
            "--cache-dir", str(cache_dir)
        ])

        # Run main()
        # Since deepseek_output.json is written in the current working directory,
        # we change directory temporarily, or mock its output path if needed.
        # Let's mock write location to prevent side-effects on current repo
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        try:
            main()

            # Verify cache_dir exists with 0o700
            assert cache_dir.exists()
            assert (os.stat(cache_dir).st_mode & 0o777) == 0o700

            # Verify deepseek_output.json exists with 0o600
            output_file = Path('deepseek_output.json')
            assert output_file.exists()
            assert (os.stat(output_file).st_mode & 0o777) == 0o600
        finally:
            os.chdir(original_cwd)

    finally:
        shutil.rmtree(temp_dir)
