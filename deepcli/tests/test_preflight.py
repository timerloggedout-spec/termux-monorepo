"""_v1_preflight scoring."""

import sys, pathlib, unittest

# __file__-relative bootstrap: import deepcli.* from THIS checkout
# (not $HOME/deepcli), so worktree-local edits are exercised.
_TESTS_DIR = pathlib.Path(__file__).resolve().parent
_REPO_ROOT = _TESTS_DIR.parent  # <checkout>/deepcli/tests -> <checkout>/deepcli (dir holding the deepcli package)
sys.path.insert(0, str(_REPO_ROOT))
from deepcli._v1_preflight import score, pattern_match, penalty_count, env_risk
from deepcli import _v1_preflight as preflight_mod


class TestPreflight(unittest.TestCase):
    def test_penalty_empty(self):
        self.assertEqual(penalty_count([]), 0)

    def test_penalty_kill(self):
        self.assertGreaterEqual(penalty_count(["KILL_AGENT"]), 10)

    def test_pattern_kill_totp(self):
        p, g = pattern_match(["KILL_AGENT", "TOTP_CALL"])
        self.assertGreaterEqual(p, 0.9)

    def test_wipe_sequence(self):
        r = score(
            ["AGENT_CACHED", "PUBRING_EMPTY", "KILL_AGENT", "AGENT_EMPTY", "TOTP_FAIL"]
        )
        self.assertIn(r["level"], ("AMBER", "RED"))

    def test_kill_unrecoverable(self):
        env = {"agent_grips": 2, "pubring_size": 32, "pass_2fa_exists": True}
        r = score([], next_action="KILL_AGENT", env=env)
        self.assertEqual(r["level"], "RED")

    def test_read_green(self):
        self.assertEqual(score([], next_action="TOTP_CALL")["level"], "GREEN")


class TestEnvRisk(unittest.TestCase):
    """env_risk() weights: agent_empty=5, pubring_empty=4, pass_2fa_missing=8."""

    def test_healthy_is_zero(self):
        s, w = env_risk(
            {"agent_grips": 3, "pubring_size": 4096, "pass_2fa_exists": True}
        )
        self.assertEqual(s, 0)
        self.assertEqual(w["agent_empty"], 0)
        self.assertEqual(w["pubring_empty"], 0)
        self.assertEqual(w["pass_2fa_missing"], 0)

    def test_agent_empty(self):
        s, w = env_risk(
            {"agent_grips": 0, "pubring_size": 4096, "pass_2fa_exists": True}
        )
        self.assertEqual(s, 5)
        self.assertEqual(w["agent_empty"], 5)

    def test_pubring_empty_below_threshold(self):
        s, w = env_risk({"agent_grips": 3, "pubring_size": 99, "pass_2fa_exists": True})
        self.assertEqual(s, 4)
        self.assertEqual(w["pubring_empty"], 4)

    def test_pubring_exactly_threshold_is_ok(self):
        s, _ = env_risk(
            {"agent_grips": 3, "pubring_size": 100, "pass_2fa_exists": True}
        )
        self.assertEqual(s, 0)

    def test_pass_2fa_missing(self):
        s, w = env_risk(
            {"agent_grips": 3, "pubring_size": 4096, "pass_2fa_exists": False}
        )
        self.assertEqual(s, 8)
        self.assertEqual(w["pass_2fa_missing"], 8)

    def test_all_three_sum_to_17(self):
        s, w = env_risk({"agent_grips": 0, "pubring_size": 0, "pass_2fa_exists": False})
        self.assertEqual(s, 17)
        self.assertEqual(sum(w.values()), 17)



class TestPublicApiMatchesDocstring(unittest.TestCase):
    """The module __doc__ 'Public API' block must not advertise names that
    do not exist. Guards against docstring/API drift (e.g. the removed
    phantom check_action() entry)."""

    def test_every_documented_public_name_exists(self):
        doc = preflight_mod.__doc__ or ""
        self.assertIn("Public API:", doc)
        api_section = doc.split("Public API:", 1)[1]
        import re
        # Lines look like:  name(args) -> dict   # comment
        names = re.findall(r"^\s*([a-zA-Z_]\w*)\(", api_section, re.M)
        self.assertTrue(names, "no public API names parsed from docstring")
        missing = [n for n in names if not hasattr(preflight_mod, n)]
        self.assertEqual(missing, [], f"docstring advertises missing names: {missing}")

    def test_check_action_is_not_advertised(self):
        # explicit pin: check_action() was never implemented and must not be
        # listed in the docstring's Public API block.
        doc = preflight_mod.__doc__ or ""
        api_section = doc.split("Public API:", 1)[1]
        self.assertNotIn("check_action", api_section)


if __name__ == "__main__":
    unittest.main()
