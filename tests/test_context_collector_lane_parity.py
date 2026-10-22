"""Offline regression contract for the two collectors in PR #1239 (RL-20)."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ("src/context_collector.py", "termux-multi-agent/src/context_collector.py")


def load_collector(path):
    spec = importlib.util.spec_from_file_location("lane_collector", ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CollectorLaneParity(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name) / "workspace"
        self.workspace.mkdir()

    def test_invalid_paths_are_rejected_before_optional_tool_probe(self):
        for source in SOURCES:
            module = load_collector(source)
            collector = module.AutomatedContextCollector(self.workspace)
            for path in ("../outside.py", "/etc/shadow", "nested\\outside.py"):
                with self.subTest(source=source, path=path):
                    with patch.object(module.shutil, "which", return_value=None) as probe:
                        with self.assertRaises(ValueError):
                            collector.generate_ast_skeleton(path)
                        probe.assert_not_called()

    def test_symlink_is_rejected_without_optional_tool(self):
        (self.workspace / "real.py").write_text("class Safe: pass\n")
        (self.workspace / "link.py").symlink_to(self.workspace / "real.py")
        for source in SOURCES:
            with self.subTest(source=source):
                module = load_collector(source)
                with patch.object(module.shutil, "which", return_value=None) as probe:
                    with self.assertRaises(ValueError):
                        module.AutomatedContextCollector(self.workspace).generate_ast_skeleton("link.py")
                    probe.assert_not_called()

    def test_parent_symlink_escape_is_rejected(self):
        outside = Path(self.temp.name) / "outside"
        outside.mkdir()
        (outside / "private.py").write_text("secret = 'fixture'\n")
        (self.workspace / "escape").symlink_to(outside, target_is_directory=True)
        for source in SOURCES:
            with self.subTest(source=source):
                module = load_collector(source)
                with patch.object(module.shutil, "which", return_value=None):
                    with self.assertRaises(ValueError):
                        module.AutomatedContextCollector(self.workspace).generate_ast_skeleton("escape/private.py")

    def test_valid_path_without_tool_is_read_only_fallback(self):
        target = self.workspace / "safe.py"
        target.write_text("class Safe: pass\n")
        for source in SOURCES:
            with self.subTest(source=source):
                module = load_collector(source)
                with patch.object(module.shutil, "which", return_value=None):
                    with patch.object(module.subprocess, "check_output") as invoke:
                        result = module.AutomatedContextCollector(self.workspace).generate_ast_skeleton("safe.py")
                        self.assertIn("Unable to trace AST", result)
                        invoke.assert_not_called()
                self.assertEqual(target.read_text(), "class Safe: pass\n")


if __name__ == "__main__":
    unittest.main()
