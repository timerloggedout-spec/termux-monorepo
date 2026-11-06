"""Atomic publication tests for Tribute status snapshots."""
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from scripts.ci import tribute_status
from scripts.ci.tribute_status import atomic_write


class AtomicStatusWriteTests(unittest.TestCase):
    def test_atomic_write_replaces_complete_contents(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "nested" / "status.json"
            target.parent.mkdir(parents=True)
            target.write_text('{"old":true}', encoding="utf-8")
            atomic_write(target, '{"generated_at":"2026-11-02T00:00:00Z"}\n')
            self.assertEqual(target.read_text(encoding="utf-8"),
                             '{"generated_at":"2026-11-02T00:00:00Z"}\n')
            self.assertEqual(list(target.parent.glob("*.tmp")), [])

    def test_failed_replace_preserves_previous_complete_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "status.json"
            target.write_text('{"old":true}', encoding="utf-8")
            with patch.object(tribute_status.os, "replace", side_effect=OSError("simulated")):
                with self.assertRaises(OSError):
                    atomic_write(target, '{"new":true}')
            self.assertEqual(target.read_text(encoding="utf-8"), '{"old":true}')
            self.assertEqual(list(target.parent.glob("*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
