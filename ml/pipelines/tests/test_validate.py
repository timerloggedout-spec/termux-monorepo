"""Schema validation tests."""
from __future__ import annotations

import unittest

from ml.pipelines.lib.errors import SchemaError
from ml.pipelines.lib.validate import require_keys, require_lane


class TestValidate(unittest.TestCase):
    def test_keys(self) -> None:
        require_keys({"a": 1}, ["a"], label="x")
        with self.assertRaises(SchemaError):
            require_keys({}, ["a"], label="x")

    def test_lane(self) -> None:
        self.assertEqual(require_lane("wait"), "wait")
        with self.assertRaises(SchemaError):
            require_lane("merge-now")


if __name__ == "__main__":
    unittest.main()
