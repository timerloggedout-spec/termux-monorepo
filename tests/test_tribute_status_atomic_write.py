"""Atomic publication tests for Tribute status snapshots."""
import tempfile
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
