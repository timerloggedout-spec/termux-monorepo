import unittest
from ml.pipelines.icm.nav import children, trail
from ml.pipelines.icm.route import route
from ml.pipelines.icm.layers import layer_of

class IcmTest(unittest.TestCase):
    def test_trail(self) -> None:
        self.assertEqual(trail("center")[0], "entry")
        self.assertIn("ml", trail("center"))
    def test_route(self) -> None:
        self.assertEqual(route("keep ML pipelines dual-gate"), "ml")
        self.assertEqual(route("Issue 175 matrix"), "hub")
    def test_layer(self) -> None:
        self.assertEqual(layer_of("gate"), "evidence")
        self.assertTrue(children("ml"))
