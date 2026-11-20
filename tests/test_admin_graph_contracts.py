"""Run the Admin Graph and Tribute PWA source contracts with stdlib unittest.

The source contract modules expose plain test functions so they remain easy to
run from local tooling. This adapter makes the mobile/PWA checks discoverable
by the repository's portable unittest gate. Node-only syntax probes stay in
the deployment-side PWA test path.
"""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load test module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AdminGraphContractTests(unittest.TestCase):
    def _run_contracts(self, path: str, name: str, excluded: set[str] | None = None):
        module = _load(path, name)
        excluded = excluded or set()
        cases = [
            (test_name, function)
            for test_name, function in vars(module).items()
            if test_name.startswith("test_")
            and callable(function)
            and test_name not in excluded
        ]
        self.assertTrue(cases, f"No contract tests discovered in {path}")
        for test_name, function in cases:
            with self.subTest(module=path, contract=test_name):
                function()

    def test_admin_graph_mobile_and_search_contracts(self):
        self._run_contracts(
            "tests/test_admin_graph_validation.py",
            "admin_graph_validation_contracts",
        )

    def test_tribute_pwa_and_admin_graph_scope_contracts(self):
        self._run_contracts(
            "tests/test_pwa_install.py",
            "tribute_pwa_install_contracts",
            excluded={"test_scripts_parse"},
        )


if __name__ == "__main__":
    unittest.main()
