"""_v1_preflight.check_action() — API-drift regression (iteration 18).

check_action() was declared in the module docstring's Public API block
but never defined. This suite pins the now-implemented contract:

  * it exists and is callable
  * it echoes the action under test in result["action"]
  * it delegates to score() (same level/reason for the same inputs)
  * it is safe to call with no env (resolves env_state() itself) and
    never trips score()'s recovery branch with a None env
  * a benign action on a healthy supplied env stays GREEN

Loading note: the harness runs every test module in one interpreter, and
the pre-existing test_*.py files insert `$HOME/deepcli` into sys.path,
which can shadow the checkout's own `deepcli` package. To stay immune to
that, this module loads `_v1_preflight.py` straight from the checkout
tree by absolute file path via importlib, so it always tests the code
under edit in this worktree — never a stale `$HOME` copy.

All paths are pure when an explicit ``env`` is supplied: no subprocess,
no network, no filesystem probe.
"""

import importlib.util
import pathlib
import unittest

_HERE = pathlib.Path(__file__).resolve()
# tests/ -> deepcli/ (repo pkg dir) -> deepcli/deepcli/_v1_preflight.py
_SRC = _HERE.parents[1] / "deepcli" / "_v1_preflight.py"
assert _SRC.exists(), "module under test missing: %s" % _SRC

_spec = importlib.util.spec_from_file_location("_v1_preflight_under_test", _SRC)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
check_action = _mod.check_action
score = _mod.score


_HEALTHY = {"agent_grips": 3, "pubring_size": 4096, "pass_2fa_exists": True}
_UNRECOVERABLE = {"agent_grips": 2, "pubring_size": 32, "pass_2fa_exists": True}


class TestCheckAction(unittest.TestCase):
    def test_is_callable(self):
        self.assertTrue(callable(check_action))

    def test_echoes_action(self):
        r = check_action("TOTP_CALL", env=_HEALTHY)
        self.assertEqual(r["action"], "TOTP_CALL")
        self.assertEqual(r["next_action"], "TOTP_CALL")

    def test_matches_score_for_same_inputs(self):
        a = check_action("KILL_AGENT", env=_UNRECOVERABLE)
        b = score([], next_action="KILL_AGENT", env=_UNRECOVERABLE)
        self.assertEqual(a["level"], b["level"])
        self.assertEqual(a["reason"], b["reason"])

    def test_unrecoverable_kill_is_red(self):
        r = check_action("KILL_AGENT", env=_UNRECOVERABLE)
        self.assertEqual(r["level"], "RED")
        self.assertIn("no recovery", r["reason"])

    def test_benign_action_on_healthy_env_is_green(self):
        r = check_action("TOTP_CALL", env=_HEALTHY)
        self.assertEqual(r["level"], "GREEN")

    def test_events_context_is_honored(self):
        # dangerous n-gram in history -> RED regardless of a healthy env
        r = check_action(
            "TOTP_CALL", events=["KILL_AGENT", "TOTP_CALL"], env=_HEALTHY
        )
        self.assertEqual(r["level"], "RED")

    def test_default_env_does_not_crash(self):
        # no env -> resolves env_state() internally; must not raise
        r = check_action("KILL_AGENT")
        self.assertIn(r["level"], ("GREEN", "AMBER", "RED"))
        self.assertEqual(r["action"], "KILL_AGENT")


if __name__ == "__main__":
    unittest.main()
