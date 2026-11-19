"""Contract tests for the PolyGlot federation starter records."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs" / "integrations" / "polyglot"

class PolyglotFederationTests(unittest.TestCase):
    def test_example_json_documents_parse(self):
        for path in sorted((BASE / "examples").glob("*.json")):
            with self.subTest(path=path.name):
                json.loads(path.read_text(encoding="utf-8"))

    def test_schema_documents_parse(self):
        for path in sorted((BASE / "schemas").glob("*.json")):
            with self.subTest(path=path.name):
                schema = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(schema.get("$schema"), "https://json-schema.org/draft/2020-12/schema")

    def test_initial_cohort_and_transport_are_registered(self):
        data = json.loads((BASE / "examples" / "technology-targets.json").read_text(encoding="utf-8"))
        ids = {item["target_id"] for item in data["targets"]}
        self.assertTrue({"rust", "cpp", "base64", "fortran", "quic"} <= ids)
        mapping = json.loads((BASE / "examples" / "mapping-quic-streams.json").read_text(encoding="utf-8"))
        self.assertEqual(mapping["capability_id"], "transport.stream.multiplexing")
        quic = next(item for item in data["targets"] if item["target_id"] == "quic")
        self.assertEqual(quic["domain"], "transport")

    def test_validator_passes(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "polyglot" / "validate_federation.py")],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

if __name__ == "__main__":
    unittest.main()
