"""_v1_events symbols."""
import sys, pathlib, unittest
sys.path.insert(0, str(pathlib.Path.home() / "deepcli"))
from deepcli._v1_events import extract

class TestEvents(unittest.TestCase):
    def test_kill(self):  self.assertIn("KILL_AGENT", extract("gpgconf --kill gpg-agent"))
    def test_read(self):  self.assertIn("CRED_READ", extract("cat ~/.gnupg/.2fa-pass"))
    def test_write(self): self.assertIn("CRED_WRITE", extract('echo pw > ~/.gnupg/.2fa-pass'))
    def test_empty(self): self.assertEqual(extract(""), [])

if __name__ == "__main__": unittest.main()
