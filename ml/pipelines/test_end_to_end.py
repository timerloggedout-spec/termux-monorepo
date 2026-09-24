import unittest
from ml.pipelines.cli import _fixture
from ml.pipelines.lanes.classify import classify_pr
from ml.pipelines.lib.types import Lane


class EndToEndTests(unittest.TestCase):
    def test_fixture_classifications(self) -> None:
        snap = _fixture()
        got = {pr["number"]: classify_pr(pr) for pr in snap["prs"]}
        self.assertEqual(got[48], Lane.HOLD)
        self.assertEqual(got[788], Lane.HOLD)
        self.assertEqual(got[785], Lane.WAIT)
        self.assertEqual(got[682], Lane.EXTRACT)
        self.assertEqual(got[432], Lane.EXTRACT)
        self.assertEqual(got[630], Lane.EXTRACT)
        self.assertEqual(got[764], Lane.HOLD)
        self.assertEqual(got[762], Lane.OBSERVE)
        self.assertEqual(got[787], Lane.SUPERSEDE)
        self.assertEqual(got[707], Lane.PROMOTE)
