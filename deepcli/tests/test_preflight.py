"""_v1_preflight scoring."""

import sys, pathlib, unittest

sys.path.insert(0, str(pathlib.Path.home() / "deepcli"))
from deepcli._v1_preflight import (
    score,
    pattern_match,
    penalty_count,
    env_risk,
    PUBRING_MIN_BYTES,
)


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

    def test_pubring_threshold_is_named_constant(self):
        # boundary is exactly PUBRING_MIN_BYTES: one byte below is risky, at it is ok
        s_below, _ = env_risk(
            {
                "agent_grips": 3,
                "pubring_size": PUBRING_MIN_BYTES - 1,
                "pass_2fa_exists": True,
            }
        )
        s_at, _ = env_risk(
            {
                "agent_grips": 3,
                "pubring_size": PUBRING_MIN_BYTES,
                "pass_2fa_exists": True,
            }
        )
        self.assertEqual(s_below, 4)
        self.assertEqual(s_at, 0)

    def test_kill_recovery_uses_named_constant(self):
        # exactly at threshold with a live grip -> NOT the empty-pubring branch
        env = {
            "agent_grips": 2,
            "pubring_size": PUBRING_MIN_BYTES,
            "pass_2fa_exists": True,
        }
        r = score([], next_action="KILL_AGENT", env=env)
        self.assertNotEqual(
            r["reason"],
            "KILL_AGENT on cached agent with empty pubring \u2014 no recovery",
        )


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
