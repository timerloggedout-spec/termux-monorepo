#!/usr/bin/env python3
"""Offline unit tests for agent.execute() dispatch semantics.

Covers the tool-error post-mortem path added in commit ae3f0cf1
("agent.py: log tool implementation errors in execute()"):
  - PermissionError / FileNotFoundError  -> "BLOCKED: ..." (NOT logged)
  - any other Exception                  -> "ERROR ..." + tool_errors.jsonl row
  - missing required args                -> arg-validation error (NOT logged)
  - unknown tool                          -> "ERROR unknown tool"
  - finish                                -> {"finished": True, ...}

These tests are fully offline: DISPATCH entries are monkeypatched and
HOME-relative paths are redirected to a tmp dir. Run with::

    python3 -m pytest deepcli/tests/test_agent_execute.py -q
or standalone::

    python3 deepcli/tests/test_agent_execute.py
"""
import json
import os
import sys
import tempfile
import importlib.util
from pathlib import Path

# Import agent.py as a module without requiring a real ~/.deepcli/hub.token.
_AGENT_PATH = Path(__file__).resolve().parent.parent / "agent.py"


def _load_agent(tmp_home: Path):
    """Load agent.py with HOME redirected so import-time file reads succeed."""
    (tmp_home / ".deepcli").mkdir(parents=True, exist_ok=True)
    (tmp_home / ".deepcli" / "hub.token").write_text("test-token\n")
    old_home = os.environ.get("HOME")
    os.environ["HOME"] = str(tmp_home)
    try:
        spec = importlib.util.spec_from_file_location("agent_under_test", _AGENT_PATH)
        mod = importlib.util.module_from_spec(spec)
        # ``import session_store`` inside agent.py is optional at import time in
        # this sandbox; if it fails we still want a clear signal.
        spec.loader.exec_module(mod)
        return mod
    finally:
        if old_home is None:
            os.environ.pop("HOME", None)
        else:
            os.environ["HOME"] = old_home


def _call(fn, arguments=""):
    return {"id": "call_1", "function": {"name": fn, "arguments": arguments}}


def _errors_log(tmp_home: Path) -> Path:
    return tmp_home / ".deepcli" / "logs" / "tool_errors.jsonl"


def test_blocked_is_not_logged():
    with tempfile.TemporaryDirectory() as d:
        tmp_home = Path(d)
        agent = _load_agent(tmp_home)

        def boom(_args):
            raise PermissionError("nope")

        agent.DISPATCH["read_file"] = boom
        out = agent.execute(_call("read_file", json.dumps({"path": "x"})))
        assert isinstance(out, str) and out.startswith("BLOCKED: PermissionError"), out
        assert not _errors_log(tmp_home).exists(), "policy blocks must NOT be logged"


def test_file_not_found_is_blocked_not_logged():
    with tempfile.TemporaryDirectory() as d:
        tmp_home = Path(d)
        agent = _load_agent(tmp_home)

        def boom(_args):
            raise FileNotFoundError("missing")

        agent.DISPATCH["read_file"] = boom
        out = agent.execute(_call("read_file", json.dumps({"path": "x"})))
        assert isinstance(out, str) and out.startswith("BLOCKED: FileNotFoundError"), out
        assert not _errors_log(tmp_home).exists(), "policy blocks must NOT be logged"


def test_generic_error_is_logged():
    with tempfile.TemporaryDirectory() as d:
        tmp_home = Path(d)
        agent = _load_agent(tmp_home)

        def boom(_args):
            raise ValueError("kaboom")

        agent.DISPATCH["read_file"] = boom
        out = agent.execute(_call("read_file", json.dumps({"path": "x"})))
        assert isinstance(out, str) and out.startswith("ERROR ValueError"), out
        log = _errors_log(tmp_home)
        assert log.exists(), "implementation errors must be logged for post-mortem"
        row = json.loads(log.read_text().strip().splitlines()[-1])
        assert row["tool"] == "read_file"
        assert row["exc"] == "ValueError"
        assert "kaboom" in row["msg"]
        assert "tb" in row and row["tb"]


def test_missing_args_not_logged():
    with tempfile.TemporaryDirectory() as d:
        tmp_home = Path(d)
        agent = _load_agent(tmp_home)
        called = {"n": 0}

        def spy(_args):
            called["n"] += 1
            return "ok"

        agent.DISPATCH["read_file"] = spy
        out = agent.execute(_call("read_file", json.dumps({})))
        assert isinstance(out, str) and out.startswith("ERROR read_file: missing required arg"), out
        assert called["n"] == 0, "dispatch must not run when args are missing"
        assert not _errors_log(tmp_home).exists()


def test_unknown_tool():
    with tempfile.TemporaryDirectory() as d:
        agent = _load_agent(Path(d))
        out = agent.execute(_call("does_not_exist", json.dumps({})))
        assert isinstance(out, str) and out == "ERROR unknown tool: does_not_exist", out


def test_bad_args_json():
    with tempfile.TemporaryDirectory() as d:
        agent = _load_agent(Path(d))
        out = agent.execute(_call("read_file", "{not json"))
        assert isinstance(out, str) and out.startswith("ERROR parsing args:"), out


def test_finish_short_circuits():
    with tempfile.TemporaryDirectory() as d:
        agent = _load_agent(Path(d))
        out = agent.execute(_call("finish", json.dumps({"summary": "all done"})))
        assert out == {"finished": True, "summary": "all done"}, out


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"  \u2705 {name}")
            except Exception as e:
                failures += 1
                print(f"  \u274c {name}: {type(e).__name__}: {e}")
    print(f"\n{'FAILED' if failures else 'OK'} ({failures} failure(s))")
    sys.exit(1 if failures else 0)
