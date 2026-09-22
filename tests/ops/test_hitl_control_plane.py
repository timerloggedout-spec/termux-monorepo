import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "scripts" / "ops"))
from hitl_control_plane import bounded_replay, make_projection, propose_command, transition, to_gource

class HITLControlPlaneTests(unittest.TestCase):
    def test_proposal_is_stable(self):
        a=propose_command("reply-to-comment","https://github.com/o/r/issues/1#issuecomment-2",["sha:abc","comment:2"])
        b=propose_command("reply-to-comment","https://github.com/o/r/issues/1#issuecomment-2",["sha:abc","comment:2"])
        self.assertEqual(a.command_id,b.command_id)
        self.assertTrue(a.approval_required)
        self.assertEqual(a.state,"DRAFT")

    def test_dispatch_requires_approval(self):
        self.assertEqual(transition("APPROVED","DISPATCHED",approved=True),"DISPATCHED")
        with self.assertRaises(PermissionError):
            transition("APPROVED","DISPATCHED")

    def test_replay_projection(self):
        events=[{"event_id":f"e{i}","occurred_at":f"2026-01-01T00:00:0{i}Z","scope":{"entity_id":f"issue:{i}"}} for i in range(4)]
        selected=bounded_replay(events,.25,.75)
        p=make_projection(selected,"abc1234","interactive")
        self.assertEqual(len(selected),2)
        self.assertEqual(p.event_count,2)
        self.assertTrue(p.snapshot_id.startswith("snapshot-"))

    def test_gource_same_range(self):
        e=[{"event_id":"e1","occurred_at":"2026-01-01T00:00:00Z","actor":{"id":"owner"},"scope":{"entity_id":"pr:7"}}]
        self.assertIn("owner|M|pr:7",to_gource(e))

if __name__=="__main__":
    unittest.main()
