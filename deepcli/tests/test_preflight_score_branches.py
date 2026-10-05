"""_v1_preflight.score() branch coverage (iteration 38).

Covers two branches that existing TestPreflight did not exercise:
  1. the pubring-unrecoverable RED branch: KILL_AGENT on an agent
     that has grips cached but whose pubring is < 100 bytes.
  2. the AMBER pattern branch: best n-gram probability in [0.80, 0.90).

Both are pure: score() takes a state dict and never shells out or
hits the network when env is supplied.

Revision 2 (iteration 45): self-locating import. A worktree run must
resolve `_v1_preflight` from *this* checkout's deepcli root; the
$HOME/deepcli path is only a last-resort fallback. The chosen bootstrap
root is asserted on-disk so the check is independent of import order
inside the unittest harness.
"""

import sys, pathlib, unittest

_HERE = pathlib.Path(__file__).resolve()
_BOOT_ROOTS = (_HERE.parents[1], pathlib.Path.home() / "deepcli")
for _root in _BOOT_ROOTS:
    if (_root / "deepcli" / "_v1_preflight.py").exists():
        sys.path.insert(0, str(_root))
        break
from deepcli._v1_preflight import score


class TestScoreBranches(unittest.TestCase):
    def test_pubring_unrecoverable_red(self):
        # grips cached (>0) but pubring < 100 -> RED, not recoverable
        env = {"agent_grips": 3, "pubring_size": 32, "pass_2fa_exists": True}
        r = score([], next_action="KILL_AGENT", env=env)
        self.assertEqual(r["level"], "RED")
        self.assertIn("no recovery", r["reason"])

    def test_pubring_unrecoverable_not_when_grips_zero(self):
        # same tiny pubring but no grips -> pubring-RED branch must not fire
        env = {"agent_grips": 0, "pubring_size": 32, "pass_2fa_exists": True}
        r = score([], next_action="KILL_AGENT", env=env)
        self.assertNotIn("no recovery", r.get("reason") or "")

    def test_pattern_amber_band(self):
        # (CRED_READ, KILL_AGENT) = 0.85 -> AMBER (0.80 <= p < 0.90)
        r = score(
            ["CRED_READ", "KILL_AGENT"],
            env={"agent_grips": 2, "pubring_size": 4096, "pass_2fa_exists": True},
        )
        self.assertEqual(r["level"], "AMBER")
        self.assertAlmostEqual(r["pattern_p"], 0.85)

    def test_pattern_red_band(self):
        # (KILL_AGENT, TOTP_CALL) = 0.95 -> RED
        r = score(
            ["KILL_AGENT", "TOTP_CALL"],
            env={"agent_grips": 2, "pubring_size": 4096, "pass_2fa_exists": True},
        )
        self.assertEqual(r["level"], "RED")

    def test_bootstrap_prefers_checkout_root(self):
        # pick _HERE.parents[1] (this checkout's deepcli) over $HOME/deepcli
        local = _HERE.parents[1] / "deepcli" / "_v1_preflight.py"
        self.assertTrue(local.exists(), "worktree _v1_preflight.py must exist")
        chosen = next(
            r for r in _BOOT_ROOTS if (r / "deepcli" / "_v1_preflight.py").exists()
        )
        self.assertEqual(chosen.resolve(), _HERE.parents[1].resolve())


if __name__ == "__main__":
    unittest.main()
