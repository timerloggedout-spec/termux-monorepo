"""_v1_events symbols."""
import sys, pathlib, unittest
sys.path.insert(0, str(pathlib.Path.home() / "deepcli"))
from deepcli._v1_events import extract

class TestEvents(unittest.TestCase):
    def test_kill(self):  self.assertIn("KILL_AGENT", extract("gpgconf --kill gpg-agent"))
    def test_read(self):  self.assertIn("CRED_READ", extract("cat ~/.gnupg/.2fa-pass"))
    def test_write(self): self.assertIn("CRED_WRITE", extract("echo pw > ~/.gnupg/.2fa-pass"))
    def test_empty(self): self.assertEqual(extract(""), [])

    def test_order_is_first_appearance_not_rule_order(self):
        # CRED_WRITE appears before KILL_AGENT in the text, but KILL_AGENT is
        # RULES[0]. The result must follow the text, not the rule table.
        s = extract("echo pw > ~/.gnupg/.2fa-pass" + chr(10) + "gpgconf --kill gpg-agent")
        self.assertEqual(s, ["CRED_WRITE", "KILL_AGENT"])

    def test_cross_category_order_preserved(self):
        # CRED_READ precedes PUBRING_DELETE in text; both are distinct rules.
        s = extract("cat ~/.gnupg/.2fa-pass" + chr(10) + "rm ~/.gnupg/pubring.kbx")
        self.assertEqual(s, ["CRED_READ", "PUBRING_DELETE"])

    def test_danger_ngram_detected_after_fix(self):
        # End-to-end: the (CRED_READ, KILL_AGENT) danger n-gram must now fire.
        from deepcli._v1_preflight import pattern_match
        s = extract("cat ~/.gnupg/.2fa-pass" + chr(10) + "gpgconf --kill gpg-agent")
        p, gram = pattern_match(s)
        self.assertGreaterEqual(p, 0.85)
        self.assertEqual(gram, ("CRED_READ", "KILL_AGENT"))

if __name__ == "__main__":
    unittest.main()
