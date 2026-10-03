"""_v1_events symbols."""

import sys, pathlib, unittest


def _repo_root():
    """Return the checkout root containing deepcli/_v1_events.py.

    Walk up from this test file; fall back to $HOME/deepcli when no
    checkout root is found so behaviour is unchanged outside a repo.
    """
    for parent in pathlib.Path(__file__).resolve().parents:
        if (parent / "deepcli" / "_v1_events.py").is_file():
            return parent
    return pathlib.Path.home() / "deepcli"


sys.path.insert(0, str(_repo_root()))
from deepcli._v1_events import extract


class TestEvents(unittest.TestCase):
    def test_kill(self):
        self.assertIn("KILL_AGENT", extract("gpgconf --kill gpg-agent"))

    def test_read(self):
        self.assertIn("CRED_READ", extract("cat ~/.gnupg/.2fa-pass"))

    def test_write(self):
        self.assertIn("CRED_WRITE", extract("echo pw > ~/.gnupg/.2fa-pass"))

    def test_empty(self):
        self.assertEqual(extract(""), [])


if __name__ == "__main__":
    unittest.main()
