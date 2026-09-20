"""CLI smoke tests."""
from __future__ import annotations

import unittest

from ml.pipelines.cli import main


class TestCli(unittest.TestCase):
    def test_status(self) -> None:
        self.assertEqual(main(["status"]), 0)

    def test_lanes(self) -> None:
        self.assertEqual(main(["lanes"]), 0)

    def test_run(self) -> None:
        self.assertEqual(main(["run"]), 0)


if __name__ == "__main__":
    unittest.main()
