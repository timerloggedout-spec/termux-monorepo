import unittest
from ml.pipelines.command_center.cycle import next_stage, wait_is_idle, STAGES

class CycleTest(unittest.TestCase):
    def test_loop(self) -> None:
        self.assertEqual(next_stage("RECON"), "IMPLEMENT")
        self.assertEqual(next_stage("REPEAT"), "RECON")
        self.assertFalse(wait_is_idle("WAIT"))
        self.assertEqual(len(STAGES), 5)
