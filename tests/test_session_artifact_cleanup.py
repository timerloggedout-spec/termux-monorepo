from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SessionArtifactCleanupTests(unittest.TestCase):
    def test_ignore_rules_cover_local_session_artifacts(self) -> None:
        ignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn(".Xauthority", ignore)
        self.assertIn(".bash_history", ignore)

    def test_tracked_session_artifacts_are_absent_from_the_working_tree(self) -> None:
        self.assertFalse((ROOT / ".Xauthority").exists())
        self.assertFalse((ROOT / ".bash_history").exists())


if __name__ == "__main__":
    unittest.main()
