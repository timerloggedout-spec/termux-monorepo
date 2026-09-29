import unittest
from ml.pipelines.actions.named_jobs import match_repo_gate, match_smoke
from ml.pipelines.actions.hygiene import is_hygiene
from ml.pipelines.actions.smoke import is_smoke

class NamedJobsTest(unittest.TestCase):
    def test_aliases(self) -> None:
        self.assertTrue(match_repo_gate("repo-gate"))
        self.assertTrue(match_repo_gate("hygiene + portability gate"))
        self.assertTrue(match_smoke("agentic termux smoke"))
        self.assertTrue(is_hygiene("hygiene + portability"))
        self.assertTrue(is_smoke("termux-smoke"))
        self.assertFalse(match_repo_gate("Vercel"))
