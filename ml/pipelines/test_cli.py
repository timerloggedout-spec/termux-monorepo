import json
import unittest
from ml.pipelines.cli import main

class CliTests(unittest.TestCase):
    def test_status(self) -> None:
        self.assertEqual(main(["status"]), 0)

    def test_lanes(self) -> None:
        self.assertEqual(main(["lanes"]), 0)

    def test_gate_blocks_48(self) -> None:
        self.assertEqual(main(["gate", "48"]), 2)
