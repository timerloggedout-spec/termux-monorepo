"""Genuine upstream orchestration test, optional and credential-free.

Run with the dedicated SDK virtualenv's Python. No real hub/provider is called.
The subprocess keeps upstream logging, cwd and environment side effects isolated.
"""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROBE = r'''
import json, os, socket
from pathlib import Path
import llm_api_hub.clients.openai_compat as hub
calls = []
def chat(messages, model, **kwargs):
    assert model == "test/local"
    assert messages and isinstance(messages[0]["content"], str)
    calls.append(Path(os.environ["WORKSPACE_DIR"]))
    return {"choices": [{"message": {"content": "Deterministic verified output."}}]}
hub.chat_completions = chat
def denied(*args, **kwargs):
    raise AssertionError("Network forbidden during SDK integration probe")
socket.socket.connect = denied
from src.swarms_adapter import run
original_cwd = Path.cwd()
for _ in range(2):
    result = run({"task": "Analyze supplied evidence, then review it.",
                  "model": "test/local", "execute": True})
    assert result["status"] == "complete"
    assert "Deterministic verified output." in json.dumps(result["output"])
    assert Path.cwd() == original_cwd
assert len(calls) == 4
assert all(not p.exists() for p in calls)
assert "WORKSPACE_DIR" not in os.environ
print(json.dumps({"status": "pass", "hub_stub_calls": len(calls),
                  "network": "forbidden", "state_removed": True}))
'''


class GenuineSwarmsSDKTests(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec("swarms"), "optional Swarms SDK not installed")
    def test_real_workflow_without_network_or_credentials(self):
        env = {"PATH": os.environ.get("PATH", ""), "LANG": "C.UTF-8",
               "PYTHONPATH": str(ROOT)}
        import tempfile
        with tempfile.TemporaryDirectory(prefix="swarms-test-home-") as home:
            env["HOME"] = home
            probe = subprocess.run([sys.executable, "-c", PROBE], cwd=home,
                                   env=env, capture_output=True, text=True, timeout=60)
        self.assertEqual(probe.returncode, 0, probe.stderr[-4000:])
        import json
        self.assertEqual(json.loads(probe.stdout)["hub_stub_calls"], 4)


if __name__ == "__main__":
    unittest.main()
