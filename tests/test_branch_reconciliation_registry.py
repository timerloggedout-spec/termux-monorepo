import importlib.util
import unittest
import subprocess
import tempfile
from pathlib import Path

spec = importlib.util.spec_from_file_location("registry", "scripts/branch_reconciliation_registry.py")
registry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(registry)


class ClassificationTests(unittest.TestCase):
    def test_identical(self):
        self.assertEqual(registry.classify(0, 0), "identical")

    def test_ahead_only(self):
        self.assertEqual(registry.classify(3, 0), "ahead-only")

    def test_behind_only(self):
        self.assertEqual(registry.classify(0, 7), "behind-only")


    def test_git_count_reads_empty_stdout_cat_file_success_correctly(self):
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["git", "init", "-q", tmp], check=True)
            def git(*args):
                return subprocess.run(["git", "-C", tmp, *args], check=True, capture_output=True, text=True).stdout.strip()
            git("config", "user.name", "BRR Test")
            git("config", "user.email", "brr@example.invalid")
            Path(tmp, "file.txt").write_text("base", encoding="utf-8")
            git("add", "file.txt")
            git("commit", "-m", "base")
            base = git("rev-parse", "HEAD")
            Path(tmp, "file.txt").write_text("head", encoding="utf-8")
            git("commit", "-am", "head")
            head = git("rev-parse", "HEAD")
            self.assertEqual(registry.git_count(base, head), (1, 0))
            self.assertEqual(registry.git_count(base, base), (0, 0))

    def test_diverged(self):
        self.assertEqual(registry.classify(2, 4), "diverged")


if __name__ == "__main__":
    unittest.main()
