import unittest

from ml.pipelines.recon08.rules import INVALID_PARKING, VALID_LANES, classify_open_pr


class RulesTest(unittest.TestCase):
    def test_vocab(self) -> None:
        self.assertTrue(VALID_LANES.isdisjoint(INVALID_PARKING))

    def test_staging_never_retarget(self) -> None:
        lane, reasons, action = classify_open_pr(
            number=48, base="master-staging", login="timerloggedout-spec", title="hub"
        )
        self.assertEqual(lane, "NEED_EVIDENCE")
        self.assertIn("wrong-base:master-staging", reasons)
        self.assertEqual(action, "never-retarget")

    def test_wholesale_kept(self) -> None:
        lane, reasons, action = classify_open_pr(
            number=682, base="master", login="timerloggedout-spec",
            title="feat(ml): keep-alive pipeline DAG",
        )
        self.assertEqual(lane, "EXTRACT")
        self.assertEqual(reasons, ("ml-wholesale-no-go",))
        self.assertEqual(action, "extract-only-keep-pipelines")

    def test_stale_recon_superseded(self) -> None:
        lane, _, action = classify_open_pr(
            number=1188, base="master", login="timerloggedout-spec", title="recon07"
        )
        self.assertEqual((lane, action), ("SUPERSEDE", "supersede-with-live-cut"))

    def test_jules_not_overwritten(self) -> None:
        lane, reasons, action = classify_open_pr(
            number=1199, base="master", login="google-labs-jules[bot]", title="Bolt"
        )
        self.assertEqual(lane, "EXTRACT")
        self.assertEqual(action, "do-not-overwrite-peer")
        self.assertEqual(reasons, ("minesweeper-peer",))


if __name__ == "__main__":
    unittest.main()
