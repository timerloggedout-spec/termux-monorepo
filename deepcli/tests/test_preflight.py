"""_v1_preflight scoring."""
import sys, pathlib, unittest


def _repo_root():
    """Walk up from this file to the dir containing deepcli/_v1_preflight.py."""
    here = pathlib.Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / "deepcli" / "_v1_preflight.py").is_file():
            return parent
    return pathlib.Path.home() / "deepcli"


_ROOT = _repo_root()
sys.path.insert(0, str(_ROOT))

# Sibling test modules that still use the old $HOME/deepcli bootstrap may have
# already imported deepcli from the main checkout in this process; drop those
# entries so we bind to THIS checkout's package.
for _name in [n for n in list(sys.modules) if n == "deepcli" or n.startswith("deepcli.")]:
    del sys.modules[_name]

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
    def test_check_action_read_is_green(self):
        from deepcli._v1_preflight import check_action
        env = {"agent_grips": 2, "pubring_size": 4096, "pass_2fa_exists": True}
        r = check_action("TOTP_CALL", env=env)
        self.assertEqual(r["action"], "TOTP_CALL")
        self.assertEqual(r["level"], "GREEN")
        self.assertTrue(r["safe"])
    def test_check_action_destructive_flags_unsafe(self):
        from deepcli._v1_preflight import check_action
        env = {"agent_grips": 2, "pubring_size": 32, "pass_2fa_exists": True}
        r = check_action("KILL_AGENT", env=env)
        self.assertFalse(r["safe"])
        self.assertIn(r["level"], ("AMBER", "RED"))
    def test_bootstrap_resolves_to_this_checkout(self):
        import deepcli._v1_preflight as m
        root = _repo_root()
        self.assertTrue((root / "deepcli" / "_v1_preflight.py").is_file())
        self.assertEqual(pathlib.Path(m.__file__).resolve(),
                         (root / "deepcli" / "_v1_preflight.py").resolve())

if __name__ == "__main__": unittest.main()
