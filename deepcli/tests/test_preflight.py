"""_v1_preflight scoring."""
import sys, pathlib, unittest


def _repo_root():
    """Walk up from this test file to the checkout root (the dir that
    contains deepcli/_v1_preflight.py). Fall back to $HOME/deepcli."""
    here = pathlib.Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "deepcli" / "_v1_preflight.py").is_file():
            return parent
    return pathlib.Path.home() / "deepcli"


sys.path.insert(0, str(_repo_root()))
# Drop any deepcli modules already imported from another checkout
# (run.py loads test modules in one process, alphabetically), so this
# module always resolves against _repo_root() above.
import sys as _sys
for _m in list(_sys.modules):
    if _m == "deepcli" or _m.startswith("deepcli."):
        del _sys.modules[_m]
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
        # regression: omitted env must not raise AttributeError; must return a level
        r = score([], next_action="KILL_AGENT")
        self.assertIn(r["level"], ("GREEN", "AMBER", "RED"))

if __name__ == "__main__": unittest.main()
