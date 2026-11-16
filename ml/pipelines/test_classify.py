import unittest
from ml.pipelines.lanes.classify import classify_pr
from ml.pipelines.lanes.vocab import Lane

class ClassifyTest(unittest.TestCase):
    def test_wrong_base(self) -> None:
        pr = {"number": 48, "title": "hub", "base": {"ref": "master-staging"}}
        self.assertEqual(classify_pr(pr), Lane.NEED_EVIDENCE)
    def test_keep_alive(self) -> None:
        pr = {"number": 682, "title": "feat(ml): keep-alive", "base": {"ref": "master"}, "keep_alive": True}
        self.assertEqual(classify_pr(pr), Lane.EXTRACT)
    def test_candidate(self) -> None:
        pr = {
            "number": 900,
            "title": "feat(ops): tiny",
            "base": {"ref": "master"},
            "gates": {"repo-gate": "success", "termux-smoke": "success"},
        }
        self.assertEqual(classify_pr(pr), Lane.CANDIDATE)
    def test_bot_extract(self) -> None:
        pr = {
            "number": 630,
            "title": "fix dashboard",
            "base": {"ref": "master"},
            "changed_files": 55,
            "user": {"login": "google-labs-jules[bot]"},
        }
        self.assertEqual(classify_pr(pr), Lane.EXTRACT)

if __name__ == "__main__":
    unittest.main()
