import unittest
from ml.pipelines.icm.layers import LAYERS, layer_of
from ml.pipelines.icm.bind import bind_cctv

class LayersTest(unittest.TestCase):
    def test_layers(self) -> None:
        self.assertEqual(LAYERS[0], "orientation")
        snap = {"master_sha": "x", "prs": []}
        bound = bind_cctv(snap, "center")
        self.assertEqual(bound["card"]["id"], "center")
        self.assertEqual(layer_of("center"), "product")
