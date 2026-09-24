import unittest
from ml.pipelines.lanes.supersede_rules import should_supersede

class SupersedeRules(unittest.TestCase):
    def test_flag(self):
        self.assertTrue(should_supersede({"supersede": True}))

    def test_pulse_title(self):
        self.assertTrue(should_supersede({"title": "ops(session): LANE-MATRIX pulse"}))

    def test_stale_keep_alive_parent(self):
        self.assertTrue(should_supersede({"keep_alive_parent": True, "stale_base": True}))

    def test_negative(self):
        self.assertFalse(should_supersede({"title": "feat(ml): keep-alive extract", "tests": True}))
