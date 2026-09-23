"""Hashing stability tests."""
from __future__ import annotations

import unittest

from ml.pipelines.lib.hashing import sha256_json


class TestHashing(unittest.TestCase):
    def test_order_independent(self) -> None:
        self.assertEqual(sha256_json({"b": 1, "a": 2}), sha256_json({"a": 2, "b": 1}))


if __name__ == "__main__":
    unittest.main()
