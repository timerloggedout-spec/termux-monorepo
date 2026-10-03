"""Regression: score() must not crash when env is omitted (None).

score(events, next_action=...) defaults env=None; env_risk(None)
falls back to the live env_state() probe. The second decision branch
(the cached-but-unrecoverable agent RED) previously called env.get()
unconditionally, raising AttributeError whenever a caller passed
next_action="KILL_AGENT" without an explicit env dict.
"""

import sys, pathlib, unittest

sys.path.insert(0, str(pathlib.Path.home() / "deepcli"))
from deepcli._v1_preflight import score


class TestScoreNoneEnv(unittest.TestCase):
    def test_kill_agent_no_env_does_not_crash(self):
        r = score(["KILL_AGENT"], next_action="KILL_AGENT")
        self.assertIn("level", r)
        self.assertIn(r["level"], ("GREEN", "AMBER", "RED"))

    def test_kill_agent_no_env_returns_expected_keys(self):
        r = score([], next_action="KILL_AGENT")
        for k in ("level", "reason", "penalty", "pattern_p", "env_score"):
            self.assertIn(k, r)

    def test_none_env_does_not_fire_unrecoverable_branch(self):
        r = score([], next_action="KILL_AGENT")
        self.assertNotIn("no recovery", r.get("reason", ""))


if __name__ == "__main__":
    unittest.main()
