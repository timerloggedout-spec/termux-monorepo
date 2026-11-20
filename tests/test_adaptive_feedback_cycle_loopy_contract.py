from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WAIT = (ROOT / ".agents/skills/adaptive-wait/SKILL.md").read_text(encoding="utf-8")
FEEDBACK = (ROOT / ".agents/skills/adaptive-feedback-cycle/SKILL.md").read_text(encoding="utf-8")


class LoopyCompatibilityTests(unittest.TestCase):
    def test_bounded_six_step_cycle_is_documented(self) -> None:
        self.assertIn("Observe → Choose → Act → Verify → Record → Repeat/stop", WAIT)

    def test_nine_route_taxonomy_is_documented(self) -> None:
        for route in ("Discover", "Find", "Audit", "Adapt", "Craft", "Run", "Debrief", "Save/Reuse", "Publish"):
            self.assertIn(route, WAIT)

    def test_terminal_state_aliases_and_approval_boundary_are_documented(self) -> None:
        for state in ("success", "clean-no-op", "clean no-op", "blocked", "approval-required", "exhausted", "stagnated"):
            self.assertIn(state, WAIT)
        self.assertIn("permission", WAIT.lower())

    def test_micro_loop_preserves_twelve_step_macro_loop(self) -> None:
        self.assertIn("Bounded micro-loop", FEEDBACK)
        self.assertIn("12-step production loop", FEEDBACK)
        self.assertIn("adaptive-wait", FEEDBACK)


if __name__ == "__main__":
    unittest.main()
