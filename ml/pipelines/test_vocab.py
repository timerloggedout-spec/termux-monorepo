import unittest
from ml.pipelines.lanes.vocab import Lane, coerce, INVALID_PARKING

class VocabTest(unittest.TestCase):
    def test_valid(self) -> None:
        self.assertEqual(coerce("EXTRACT"), Lane.EXTRACT)
    def test_parking_rejected(self) -> None:
        for raw in INVALID_PARKING:
            with self.assertRaises(ValueError):
                coerce(raw)

if __name__ == "__main__":
    unittest.main()
