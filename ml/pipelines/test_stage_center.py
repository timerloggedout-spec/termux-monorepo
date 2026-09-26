import unittest
from ml.pipelines.stages.command_center import stage_command_center
from ml.pipelines.stages.bind import stage_bind

class StageCenterTest(unittest.TestCase):
    def test_stage(self) -> None:
        ctx = {"snapshot": {"master_sha": "8d36f149", "prs": []}, "checks": [
            {"name": "repo gate", "conclusion": "success"},
            {"name": "termux smoke", "conclusion": "success"},
        ]}
        stage_bind(ctx)
        stage_command_center(ctx)
        self.assertIn("hub", ctx)
        self.assertEqual(ctx["bind"]["dual_gate"], "GREEN")
