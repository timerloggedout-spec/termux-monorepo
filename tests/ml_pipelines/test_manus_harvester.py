import json
import unittest
from pathlib import Path

from probes.manus.harvester.normalize import dedup_events, normalize_event
from probes.manus.harvester.schema import HarvesterError, validate_event

FIX = Path(__file__).resolve().parents[2] / "probes/manus/fixtures/sample-session.jsonl"


class HarvesterTests(unittest.TestCase):
    def test_fixture_normalizes_and_dedups(self):
        events = [
            normalize_event(json.loads(line))
            for line in FIX.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        deduped = dedup_events(events)
        self.assertEqual(len(events), 5)
        self.assertEqual(len(deduped), 4)
        for event in deduped:
            validate_event(event)

    def test_strips_forbidden_payload_keys(self):
        event = normalize_event(
            {
                "event_id": "e",
                "session_id": "s",
                "turn_id": 0,
                "ts": "t",
                "type": "action",
                "actor": "agent",
                "payload": {"tool": "x", "token": "nope"},
                "stream_seq": 1,
                "raw_ref": "r",
            }
        )
        self.assertNotIn("token", event["payload"])

    def test_rejects_bad_type(self):
        with self.assertRaises(HarvesterError):
            normalize_event(
                {
                    "event_id": "e",
                    "session_id": "s",
                    "turn_id": 0,
                    "ts": "t",
                    "type": "exploit",
                    "actor": "agent",
                    "payload": {},
                    "stream_seq": 1,
                    "raw_ref": "r",
                }
            )


if __name__ == "__main__":
    unittest.main()
