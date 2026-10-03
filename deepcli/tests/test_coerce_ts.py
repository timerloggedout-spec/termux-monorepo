"""Direct coverage for _v1_cache._coerce_ts (timestamp coercion)."""

import sys, pathlib, unittest

sys.path.insert(0, str(pathlib.Path.home() / "deepcli"))
from deepcli._v1_cache import _coerce_ts


class TestCoerceTs(unittest.TestCase):
    def test_none_returns_none(self):
        self.assertIsNone(_coerce_ts(None))

    def test_positive_int(self):
        self.assertEqual(_coerce_ts(1700000000), 1700000000.0)

    def test_positive_float(self):
        self.assertAlmostEqual(_coerce_ts(1700000000.5), 1700000000.5, places=6)

    def test_zero_and_negative_int_return_none(self):
        # int/float branch requires v > 0; epoch <= 0 is not a valid ts.
        self.assertIsNone(_coerce_ts(0))
        self.assertIsNone(_coerce_ts(-1))

    def test_numeric_string_is_coerced_via_float(self):
        # The str branch tries float() first, so "1700000000" -> 1700000000.0
        self.assertEqual(_coerce_ts("1700000000"), 1700000000.0)

    def test_numeric_string_zero_is_zero_not_none(self):
        # Float-branch asymmetry: str "0" -> 0.0 (via float()), not None.
        self.assertEqual(_coerce_ts("0"), 0.0)

    def test_iso_z_suffix(self):
        self.assertAlmostEqual(
            _coerce_ts("2026-10-03T00:00:00Z"),
            1790985600.0,
            delta=1.0,
        )

    def test_iso_naive_assumed_utc(self):
        # Naive ISO is assumed UTC; must equal the Z form above.
        self.assertAlmostEqual(
            _coerce_ts("2026-10-03T00:00:00"),
            _coerce_ts("2026-10-03T00:00:00Z"),
            places=6,
        )

    def test_garbage_string_returns_none(self):
        self.assertIsNone(_coerce_ts("not-a-timestamp"))

    def test_non_string_non_number_returns_none(self):
        # dicts/lists are not coercible timestamps.
        self.assertIsNone(_coerce_ts({"t": 1}))
        self.assertIsNone(_coerce_ts([1, 2, 3]))


if __name__ == "__main__":
    unittest.main()
