"""Contract tests for the Mobile Agent Testers evidence adapter."""
import json
import tempfile
import unittest
from pathlib import Path

from scripts.integrations.mobile_agent_testers_adapter import normalize, safe_text


class MobileAgentTestersAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.findings = self.root / "results-anna" / "results" / "anna" / "findings.json"
        self.findings.parent.mkdir(parents=True)
        self.findings.write_text(json.dumps({
            "score": 8,
            "issues": [
                {
                    "title": "Button exposes user@example.com and token=abcdEFGH12345678",
                    "severity": "major",
                    "screen": "Today",
                    "screens": ["01"],
                    "description": "raw private report text must stay local",
                },
                {"title": "Keyboard covers Save", "severity": "minor", "screen": "Plan"},
            ],
        }), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_emits_schema_shaped_events_without_raw_report(self):
        events, diagnostics = normalize(
            self.root, run_id="12345", repository="timerloggedout-spec/termux-monorepo",
            commit="abcdef0123456789",
        )
        self.assertEqual(diagnostics, [])
        self.assertEqual(len(events), 2)
        event = events[0]
        self.assertEqual(event["schema_version"], "1.0.0")
        self.assertEqual(event["integration_id"], "mobile-agent-testers")
        self.assertEqual(event["event_type"], "mobile_test.finding")
        self.assertEqual(event["source"]["commit_sha"], "abcdef0123456789")
        self.assertEqual(event["outcome"]["state"], "observed")
        self.assertEqual(event["evidence"]["validation_status"], "pending")
        self.assertEqual(event["provenance"]["attribution"], "provider_reported")
        self.assertIn("persona=anna", event["provenance"]["capture_method"])
        self.assertFalse(event["privacy"]["contains_raw_prompt"])
        self.assertFalse(event["privacy"]["contains_secret"])
        self.assertNotIn("description", event)
        self.assertNotIn("user@example.com", json.dumps(event))
        self.assertNotIn("abcdEFGH12345678", json.dumps(event))
        self.assertTrue(event["evidence"]["artifact_refs"][0].startswith("sha256:"))

    def test_events_match_repository_integration_schema(self):
        schema_path = Path(__file__).resolve().parents[1] / "docs" / "integrations" / "schemas" / "integration-event.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        events, _ = normalize(self.root, run_id="schema-check", repository="owner/repo")
        for event in events:
            self.assertTrue(set(schema["required"]).issubset(event))
            self.assertTrue(set(event).issubset(schema["properties"]))
            for key, value in event.items():
                definition = schema["properties"][key]
                if definition.get("type") == "object":
                    self.assertTrue(set(definition.get("required", [])).issubset(value))
                    self.assertTrue(set(value).issubset(definition["properties"]))
                    for child, child_value in value.items():
                        child_definition = definition["properties"][child]
                        if "const" in child_definition:
                            self.assertEqual(child_value, child_definition["const"])
                        if "enum" in child_definition:
                            self.assertIn(child_value, child_definition["enum"])

    def test_event_ids_and_idempotency_are_stable(self):
        first, _ = normalize(self.root, run_id="run-1", repository="owner/repo")
        second, _ = normalize(self.root, run_id="run-1", repository="owner/repo")
        self.assertEqual(
            [e["event_id"] for e in first],
            [e["event_id"] for e in second],
        )
        self.assertEqual(
            [e["idempotency_key"] for e in first],
            [e["idempotency_key"] for e in second],
        )

    def test_bad_files_and_bad_issues_are_skipped(self):
        self.findings.write_text("{broken", encoding="utf-8")
        events, diagnostics = normalize(self.root, run_id="run-2", repository="owner/repo")
        self.assertEqual(events, [])
        self.assertTrue(any("malformed" in item for item in diagnostics))

    def test_text_redaction_and_bounds(self):
        value = safe_text("mail user@example.com call +1 (555) 123-4567", 80)
        self.assertNotIn("user@example.com", value)
        self.assertNotIn("555", value)
        self.assertLessEqual(len(value), 80)


if __name__ == "__main__":
    unittest.main()
