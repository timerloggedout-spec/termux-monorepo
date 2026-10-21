import unittest
from ml.pipelines.lanes.extract_family import family_of, must_extract

class ExtractFamilyTest(unittest.TestCase):
    def test_families(self) -> None:
        self.assertEqual(family_of(48), "staging-only")
        self.assertEqual(family_of(432), "ml-wholesale")
        self.assertEqual(family_of(630), "minesweeper")
        self.assertTrue(must_extract(682))
        self.assertFalse(must_extract(848))
