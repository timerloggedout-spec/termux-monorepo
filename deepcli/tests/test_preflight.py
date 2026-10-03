"""_v1_preflight scoring."""
import sys, pathlib, unittest
def _repo_root():
    p = pathlib.Path(__file__).resolve()
    for parent in [p.parent] + list(p.parents):
        if (parent / "deepcli" / "_v1_preflight.py").exists():
            return parent
    return pathlib.Path.home() / "deepcli"
sys.path.insert(0, str(_repo_root()))
from deepcli._v1_preflight import score, pattern_match, penalty_count, check_action

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
    def test_check_action_is_public_api(self):
        # check_action is declared in the module docstring; it must exist.
        self.assertTrue(callable(check_action))

    def test_check_action_kill_unrecoverable_red(self):
        env = {"agent_grips": 2, "pubring_size": 32, "pass_2fa_exists": True}
        r = check_action("KILL_AGENT", [], env=env)
        self.assertEqual(r["level"], "RED")
        self.assertEqual(r["next_action"], "KILL_AGENT")

    def test_check_action_benign_green(self):
        env = {"agent_grips": 2, "pubring_size": 2048, "pass_2fa_exists": True}
        r = check_action("TOTP_CALL", [], env=env)
        self.assertEqual(r["level"], "GREEN")

if __name__ == "__main__": unittest.main()
