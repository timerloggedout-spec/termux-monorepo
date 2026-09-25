"""Structural test: temporal smoke module imports when temporalio is present.

Skips cleanly when temporalio is not installed so dual-gate hosts without the
optional dependency stay green.
"""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


class TemporalHelloImportTest(unittest.TestCase):
    def test_script_file_exists(self) -> None:
        root = Path(__file__).resolve().parents[1]
        script = root / "scripts" / "temporal" / "hello_workflow.py"
        self.assertTrue(script.is_file(), f"missing {script}")

    def test_optional_temporalio_gate(self) -> None:
        if importlib.util.find_spec("temporalio") is None:
            self.skipTest("temporalio not installed (optional capability)")
        root = Path(__file__).resolve().parents[1]
        script = root / "scripts" / "temporal" / "hello_workflow.py"
        spec = importlib.util.spec_from_file_location("hello_workflow", script)
        self.assertIsNotNone(spec)
        assert spec is not None and spec.loader is not None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertTrue(callable(mod.main))


if __name__ == "__main__":
    unittest.main()
