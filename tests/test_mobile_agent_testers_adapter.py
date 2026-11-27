"""Contract tests for the Mobile Agent Testers evidence adapter."""
import json
import tempfile
import unittest
from pathlib import Path

from argparse import ArgumentTypeError

from scripts.integrations.mobile_agent_testers_adapter import iso_datetime, main, normalize, safe_text


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
                None,
                {"title": "", "severity": "minor"},
            ],
        }), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_emits_schema_shaped_events_without_raw_report(self):
        events, diagnostics, valid_files, valid_personas = normalize(
            self.root, run_id="12345", repository="timerloggedout-spec/termux-monorepo",
            commit="abcdef0123456789",
        )
        self.assertEqual(len(events), 2)
        self.assertEqual(len(diagnostics), 2)
        self.assertEqual(valid_files, 1)
        self.assertEqual(valid_personas, {"anna"})
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
        events, _, valid_files, valid_personas = normalize(self.root, run_id="schema-check", repository="owner/repo")
        self.assertEqual(valid_files, 1)
        self.assertEqual(valid_personas, {"anna"})
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
        first, _, first_files, first_personas = normalize(self.root, run_id="run-1", repository="owner/repo")
        second, _, second_files, second_personas = normalize(self.root, run_id="run-1", repository="owner/repo")
        self.assertEqual(first_files, 1)
        self.assertEqual(second_files, 1)
        self.assertEqual(first_personas, {"anna"})
        self.assertEqual(second_personas, {"anna"})
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
        events, diagnostics, valid_files, valid_personas = normalize(self.root, run_id="run-2", repository="owner/repo")
        self.assertEqual(events, [])
        self.assertEqual(valid_files, 0)
        self.assertEqual(valid_personas, set())
        self.assertTrue(any("malformed" in item for item in diagnostics))

    def test_valid_empty_findings_file_is_distinct_from_missing_evidence(self):
        self.findings.write_text(json.dumps({"score": 10, "issues": []}), encoding="utf-8")
        events, diagnostics, valid_files, valid_personas = normalize(self.root, run_id="empty-run", repository="owner/repo")
        self.assertEqual(events, [])
        self.assertEqual(diagnostics, [])
        self.assertEqual(valid_files, 1)
        self.assertEqual(valid_personas, {"anna"})

    def test_incomplete_collection_preserves_existing_output(self):
        self.findings.write_text("{broken", encoding="utf-8")
        output = self.root / "events.jsonl"
        self.assertEqual(
            main(["--run-dir", str(self.root), "--run-id", "missing-run", "--expected-personas", "anna", "--output", str(output)]),
            3,
        )
        self.assertFalse(output.exists())

    def test_missing_findings_file_is_incomplete(self):
        self.findings.unlink()
        output = self.root / "events.jsonl"
        self.assertEqual(
            main(["--run-dir", str(self.root), "--run-id", "missing-file", "--expected-personas", "anna", "--output", str(output)]),
            3,
        )
        self.assertFalse(output.exists())

    def test_partial_persona_collection_is_incomplete(self):
        output = self.root / "events.jsonl"
        self.assertEqual(
            main([
                "--run-dir", str(self.root), "--run-id", "partial-run",
                "--expected-personas", "anna,malik", "--output", str(output),
            ]),
            3,
        )
        self.assertFalse(output.exists())

    def test_existing_output_requires_explicit_overwrite(self):
        output = self.root / "events.jsonl"
        output.write_text("preserve", encoding="utf-8")
        self.assertEqual(
            main(["--run-dir", str(self.root), "--run-id", "run-1", "--expected-personas", "anna", "--output", str(output)]),
            4,
        )
        self.assertEqual(output.read_text(encoding="utf-8"), "preserve")

    def test_overwrite_writes_atomically_after_valid_collection(self):
        output = self.root / "events.jsonl"
        output.write_text("stale", encoding="utf-8")
        self.assertEqual(
            main(["--run-dir", str(self.root), "--run-id", "run-1", "--expected-personas", "anna", "--output", str(output), "--overwrite"]),
            0,
        )
        lines = output.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 2)
        self.assertTrue(all(json.loads(line)["event_type"] == "mobile_test.finding" for line in lines))

    def test_timestamps_require_timezone_aware_iso8601(self):
        self.assertEqual(iso_datetime("2026-11-23T21:00:00Z"), "2026-11-23T21:00:00Z")
        with self.assertRaises(ArgumentTypeError):
            iso_datetime("2026-11-23T21:00:00")
        with self.assertRaises(ArgumentTypeError):
            iso_datetime("2026-11-23T21:00Z")

    def test_text_redaction_and_bounds(self):
        value = safe_text("mail user@example.com call +1 (555) 123-4567", 80)
        self.assertNotIn("user@example.com", value)
        self.assertNotIn("555", value)
        self.assertLessEqual(len(value), 80)
        token = "ghp_" + ("A" * 36)
        self.assertNotIn(token, safe_text(token, 100))


if __name__ == "__main__":
    unittest.main()
