import unittest
from ml.pipelines.command_center.peers import active_peers, peer_of

class PeersCenterTest(unittest.TestCase):
    def test_jules(self) -> None:
        self.assertEqual(peer_of("google-labs-jules[bot]"), "jules")
    def test_active(self) -> None:
        prs = [{"number": 630, "user": {"login": "google-labs-jules[bot]"}}]
        self.assertIn(630, active_peers(prs)["jules"])
