import unittest
from ml.pipelines.command_center.hub import emit_hub
from ml.pipelines.command_center.constants import INVALID_PARKING, VOCAB
from ml.pipelines.command_center.schema import validate_snapshot

class CommandCenterTest(unittest.TestCase):
    def test_hub_vocab(self) -> None:
        snap = {"master_sha": "8d36f149", "observed_at": "2026-09-26T21:15Z", "session": "t",
                "prs": [{"number": 900, "title": "feat(ops): tiny", "base": {"ref": "master"},
                         "gates": {"repo-gate": "success", "termux-smoke": "success"}}]}
        hub = emit_hub(snap)
        self.assertEqual(hub["kind"], "command-center")
        self.assertFalse(hub["pulse_comment"])
        counts = hub["payload"]["board"]["counts"]
        for lane in VOCAB:
            self.assertIn(lane, counts)
        for bad in INVALID_PARKING:
            self.assertNotIn(bad, counts)

    def test_invalid_snapshot_parking(self) -> None:
        snap = {"master_sha": "x", "observed_at": "t", "session": "s",
                "prs": [{"number": 1, "lane": "HOLD"}]}
        self.assertTrue(any("invalid-parking" in e for e in validate_snapshot(snap)))
