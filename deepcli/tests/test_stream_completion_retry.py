#!/usr/bin/env python3
"""Offline regression test: stream_completion must not reference an undefined
name on the all-retries-exhausted path.

Historically the function ended with ``return final_text`` where ``final_text``
was never assigned, so exhausting every retry raised NameError instead of
returning cleanly.  This test exercises that terminal branch directly, without
network access, by injecting stub implementations of the helpers
``stream_completion`` depends on.
"""
import importlib
import pathlib
import sys
import types
import unittest


def _repo_root():
    """Walk up from this file to the dir containing deepcli/deepcli/core.py."""
    here = pathlib.Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / "deepcli" / "deepcli" / "core.py").is_file():
            return parent
    return None


class _FakeResp:
    status_code = 500
    text = "server exploded"
    content = b""


class _FakeSession:
    headers = {}

    def post(self, *args, **kwargs):
        return _FakeResp()


class StreamCompletionRetryTest(unittest.TestCase):
    def _load_core(self):
        root = _repo_root()
        if root is None:
            self.skipTest("deepcli package root not found relative to test file")
        sys.path.insert(0, str(root))
        # Ensure we bind to THIS checkout rather than any $HOME copy.
        for name in [n for n in list(sys.modules) if n == "deepcli" or n.startswith("deepcli.")]:
            del sys.modules[name]
        return importlib.import_module("deepcli.deepcli.core")

    def test_no_undefined_final_text(self):
        core = self._load_core()
        src = pathlib.Path(core.__file__).read_text()
        self.assertNotIn(
            "return final_text",
            src,
            "stream_completion still references undefined 'final_text'",
        )

    def test_retry_exhaustion_returns_empty_string(self):
        core = self._load_core()

        # Neutralise the network / POW layers with deterministic stubs.
        core.get_pow_challenge = lambda *a, **k: {"challenge": "c"}
        core.solve_pow = lambda *a, **k: "pow"
        core.get_session = lambda *a, **k: _FakeSession()
        core._log_retry = lambda *a, **k: None
        # Keep the retry loop short so the test is fast.
        core.time.sleep = lambda *a, **k: None

        # Patch module-level constants consulted inside the loop if present.
        orig_max = getattr(core, "max_retries", None)

        try:
            # Shrink max_retries by rebinding via source-compiled closure is not
            # possible; instead just let it run 8 quick iterations with no sleep.
            result = core.stream_completion("tok", "hi", "sid", auto_retry=True)
        finally:
            if orig_max is not None:
                core.max_retries = orig_max

        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()
