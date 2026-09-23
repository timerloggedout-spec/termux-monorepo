"""Providence attribution tests."""
from __future__ import annotations

import unittest

from ml.pipelines.providence.attribution import make_attribution


class TestAttribution(unittest.TestCase):
    def test_ok(self) -> None:
        row = make_attribution({"actor": "grok", "role": "administrator", "issue": 175})
        self.assertEqual(row.actor, "grok")

    def test_rejects_token_actor(self) -> None:
        with self.assertRaises(ValueError):
            make_attribution({"actor": "OPERATOR_TOKEN", "role": "operator"})


if __name__ == "__main__":
    unittest.main()
