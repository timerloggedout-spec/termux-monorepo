"""_v1_preflight scoring.

Revision 2 (iteration 48): self-locating import. A worktree run must
resolve `_v1_preflight` from *this* checkout's deepcli root; the
$HOME/deepcli path is only a last-resort fallback. The previous bootstrap
inserted ``$HOME/deepcli`` unconditionally, so a worktree run imported the
MAIN checkout's ``_v1_preflight`` instead of the worktree's. The chosen
bootstrap root is asserted on-disk so the check is independent of import
order inside the unittest harness.
"""

import sys, pathlib, unittest


def _repo_root():
    """Walk up from this test file to the checkout that owns deepcli/.

    Resolve ``__file__``-relative first, fall back to the old
    ``$HOME/deepcli`` location only when no checkout root is found.
    """
    here = pathlib.Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "deepcli" / "_v1_preflight.py").is_file():
            return parent
    return pathlib.Path.home() / "deepcli"


sys.path.insert(0, str(_repo_root()))
from deepcli._v1_preflight import score, pattern_match, penalty_count, env_risk


class TestBootstrap(unittest.TestCase):
    def test_bootstrap_resolves_to_this_checkout(self):
        root = _repo_root()
        self.assertTrue((root / "deepcli" / "_v1_preflight.py").is_file())
        self.assertIn(root, pathlib.Path(__file__).resolve().parents)


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


if __name__ == "__main__":
    unittest.main()
