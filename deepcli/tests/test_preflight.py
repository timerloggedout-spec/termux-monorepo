"""_v1_preflight scoring."""

import sys, pathlib, unittest


def _repo_root():
    """Walk up from this file to the dir containing deepcli/_v1_preflight.py.

    Ensures a worktree run imports *this* checkout's _v1_preflight, not the
    main checkout via $HOME/deepcli. $HOME/deepcli is only a last-resort
    fallback when no checkout root is found.
    """
    here = pathlib.Path(__file__).resolve()
    for d in here.parents:
        if (d / "deepcli" / "_v1_preflight.py").is_file():
            return d
    return pathlib.Path.home() / "deepcli"


sys.path.insert(0, str(_repo_root()))
from deepcli._v1_preflight import score, pattern_match, penalty_count


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

    def test_bootstrap_resolves_to_this_checkout(self):
        """Regression: _repo_root() must resolve under this test's checkout."""
        root = _repo_root()
        here = pathlib.Path(__file__).resolve()
        self.assertTrue(
            (root / "deepcli" / "_v1_preflight.py").is_file(),
            f"_repo_root() -> {root} has no deepcli/_v1_preflight.py",
        )
        self.assertTrue(
            str(here).startswith(str(root)),
            f"test file {here} is not under resolved root {root}",
        )


if __name__ == "__main__":
    unittest.main()
