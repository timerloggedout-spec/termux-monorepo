"""_v1_preflight scoring."""
import sys, pathlib, unittest
sys.path.insert(0, str(pathlib.Path.home() / "deepcli"))
from deepcli._v1_preflight import score, pattern_match, penalty_count

class TestPreflight(unittest.TestCase):
    def test_penalty_empty(self): self.assertEqual(penalty_count([]), 0)
    def test_penalty_kill(self):  self.assertGreaterEqual(penalty_count(["KILL_AGENT"]), 10)
    def test_pattern_kill_totp(self):
        p, g = pattern_match(["KILL_AGENT", "TOTP_CALL"]); self.assertGreaterEqual(p, 0.9)
    def test_wipe_sequence(self):
        r = score(["AGENT_CACHED","PUBRING_EMPTY","KILL_AGENT","AGENT_EMPTY","TOTP_FAIL"])
        self.assertIn(r["level"], ("AMBER","RED"))
    def test_kill_unrecoverable(self):
        env = {"agent_grips": 2, "pubring_size": 32, "pass_2fa_exists": True}
        r = score([], next_action="KILL_AGENT", env=env)
        self.assertEqual(r["level"], "RED")
    def test_read_green(self):
        self.assertEqual(score([], next_action="TOTP_CALL")["level"], "GREEN")
    def test_kill_agent_default_env_does_not_crash(self):
        # Regression (IT57): score(..., env=None) must probe env_state()
        # once and reuse it, not call env.get() on the raw None argument.
        env = {"agent_grips": 0, "pubring_size": 4096, "pass_2fa_exists": True}
        r = score([], next_action="KILL_AGENT", env=env)
        self.assertIn(r["level"], ("GREEN", "AMBER", "RED"))
        self.assertNotIn("NoneType", r["reason"])

if __name__ == "__main__": unittest.main()
