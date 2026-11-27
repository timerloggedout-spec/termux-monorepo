"""Exact-ratio and polyphonic overlay regressions."""
import sys
import unittest
from fractions import Fraction
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from deepcli.observatory.rhythm import RhythmicLayer, common_subdivision, exact_ratio, overlay_layers, rational_lcm

class RhythmTests(unittest.TestCase):
    def test_ratio_reduction(self):
        self.assertEqual(exact_ratio(6, 8), Fraction(3, 4))
    def test_common_subdivision(self):
        self.assertEqual(common_subdivision([Fraction(1, 2), Fraction(1, 3), Fraction(1, 5)]), 30)
    def test_rational_supercycle(self):
        self.assertEqual(rational_lcm([Fraction(1, 3), Fraction(1, 2)]), Fraction(1, 1))
    def test_three_two_polyrhythm(self):
        result = overlay_layers([
            RhythmicLayer("triple", Fraction(1, 3), (Fraction(0),)),
            RhythmicLayer("duple", Fraction(1, 2), (Fraction(0),)),
        ])
        self.assertEqual(result.supercycle, Fraction(1))
        self.assertEqual(result.subdivision, 6)
        self.assertEqual([event.at for event in result.onsets],
                         [Fraction(0), Fraction(0), Fraction(1, 3), Fraction(1, 2), Fraction(2, 3)])
        self.assertEqual(result.coincidences, ((Fraction(0), ("duple", "triple")),))
    def test_phase_displacement(self):
        result = overlay_layers([
            RhythmicLayer("bass", Fraction(1, 2), (Fraction(0),)),
            RhythmicLayer("melody", Fraction(1, 3), (Fraction(0),), Fraction(1, 6)),
        ])
        self.assertEqual(result.supercycle, Fraction(1))
        self.assertIn(Fraction(1, 6), [event.at for event in result.onsets])
    def test_invalid_ratio_and_layer(self):
        with self.assertRaises(ValueError):
            exact_ratio(1, 0)
        with self.assertRaises(ValueError):
            RhythmicLayer("bass", Fraction(1, 3), (Fraction(1, 2),))
    def test_empty_overlay_rejected(self):
        with self.assertRaises(ValueError):
            overlay_layers([])

if __name__ == "__main__":
    unittest.main()
