import unittest
from ml.pipelines.lib.io import load_json
from ml.pipelines.lib.latest import latest_session_path
from ml.pipelines.viz.cctv import emit_cctv

class CctvTest(unittest.TestCase):
    def test_ssot_projection(self) -> None:
        payload = emit_cctv(load_json(latest_session_path()))
        self.assertEqual(payload["ssot"]["lane_project"], "ops/tracking/tracking.json")
        self.assertEqual(payload["operator"], "READ_MODEL")
        self.assertNotIn("issue", payload)
        self.assertIn("EXTRACT", payload["lanes"])

if __name__ == "__main__":
    unittest.main()
