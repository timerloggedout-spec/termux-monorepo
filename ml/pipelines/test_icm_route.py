import unittest
from ml.pipelines.icm.route import route
from ml.pipelines.icm.nav import trail

class IcmRouteTest(unittest.TestCase):
    def test_cctv(self) -> None:
        self.assertEqual(route("run cctv projection"), "cctv-skill")
        self.assertEqual(trail("cctv-skill")[0], "entry")
