import unittest

from ml.pipelines.recon07.families import family_of, forbidden_actions


class FamiliesTest(unittest.TestCase):
    def test_locks(self) -> None:
        self.assertEqual(family_of(432), "wholesale-ml")
        self.assertIn("wholesale-merge", forbidden_actions(682))
        self.assertEqual(family_of(630), "minesweeper")
        self.assertIn("overwrite-peer", forbidden_actions(1185))
        self.assertIn("retarget-master", forbidden_actions(48))
        self.assertIn("treat-as-promote-gate", forbidden_actions(1025))
        self.assertEqual(family_of(1), "unscoped")


if __name__ == "__main__":
    unittest.main()
