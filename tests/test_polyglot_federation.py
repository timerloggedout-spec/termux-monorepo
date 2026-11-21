"""Contract tests for the PolyGlot federation starter records."""
from __future__ import annotations

import json
import hashlib
import re
import shutil
import tempfile
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

    def test_feed_builder_emits_content_addressed_records(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "feed.json"
            revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
            command = [
                sys.executable, str(ROOT / "scripts" / "polyglot" / "build_feed.py"),
                "--repository", "timerloggedout-spec/termux-monorepo",
                "--revision", revision,
                "--generated-at", "2026-11-19T00:00:00Z",
                "--output", str(output),
            ]
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            feed = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(feed["schema_version"], "1.0.0")
            self.assertGreaterEqual(len(feed["records"]), 7)
            canonical = json.dumps(feed["records"], sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
            self.assertEqual(feed["artifact_digest"], "sha256:" + hashlib.sha256(canonical).hexdigest())
            self.assertTrue(all(record["content_digest"].startswith("sha256:") for record in feed["records"]))
            for record in feed["records"]:
                source = subprocess.check_output(["git", "show", f"{revision}:{record['path']}"], cwd=ROOT)
                self.assertEqual(record["content_digest"], "sha256:" + hashlib.sha256(source).hexdigest())


    def test_validator_rejects_dangling_capability_and_target_references(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            fixture = root / "docs" / "integrations" / "polyglot"
            shutil.copytree(BASE, fixture)
            targets_path = fixture / "examples" / "technology-targets.json"
            targets = json.loads(targets_path.read_text(encoding="utf-8"))
            targets["targets"][-1]["capability_ids"] = ["missing.capability"]
            targets_path.write_text(json.dumps(targets), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "polyglot" / "validate_federation.py"), "--root", str(root)],
                capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unknown capability_id", result.stderr)

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            fixture = root / "docs" / "integrations" / "polyglot"
            shutil.copytree(BASE, fixture)
            mapping_path = fixture / "examples" / "mapping-quic-streams.json"
            mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
            mapping["target_id"] = "missing-target"
            mapping_path.write_text(json.dumps(mapping), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "polyglot" / "validate_federation.py"), "--root", str(root)],
                capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("target_id does not resolve", result.stderr)


    def test_validator_rejects_non_string_target_ids(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            fixture = root / "docs" / "integrations" / "polyglot"
            shutil.copytree(BASE, fixture)
            targets_path = fixture / "examples" / "technology-targets.json"
            targets = json.loads(targets_path.read_text(encoding="utf-8"))
            targets["targets"][0]["target_id"] = 144
            targets_path.write_text(json.dumps(targets), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "polyglot" / "validate_federation.py"), "--root", str(root)],
                capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("invalid target_id", result.stderr)

    def test_validator_accepts_numeric_transport_target_ids(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            fixture = root / "docs" / "integrations" / "polyglot"
            shutil.copytree(BASE, fixture)
            targets_path = fixture / "examples" / "technology-targets.json"
            targets = json.loads(targets_path.read_text(encoding="utf-8"))
            targets["targets"][0]["target_id"] = "14.4-kbps-modem"
            targets_path.write_text(json.dumps(targets), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "polyglot" / "validate_federation.py"), "--root", str(root)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


    def test_benchmark_schema_enforces_variance_and_correctness_gate(self):
        schema = json.loads((BASE / "schemas" / "benchmark-result.schema.json").read_text(encoding="utf-8"))
        measurement = schema["properties"]["measurements"]["items"]
        self.assertIn("variance", measurement["required"])
        self.assertEqual(measurement["properties"]["variance"]["minimum"], 0)
        above_gate = next(rule for rule in schema["allOf"] if rule.get("if", {}).get("properties", {}).get("parity_status", {}).get("const") == "above")
        self.assertEqual(above_gate["then"]["properties"]["correctness"]["const"], "pass")
        self.assertEqual(above_gate["then"]["properties"]["advantage_claim"]["type"], "string")
        nonpass_gate = next(rule for rule in schema["allOf"] if rule.get("if", {}).get("properties", {}).get("correctness", {}).get("const") == "pass")
        self.assertEqual(nonpass_gate["else"]["properties"]["parity_status"]["enum"], ["unknown"])
        self.assertEqual(nonpass_gate["else"]["properties"]["advantage_claim"]["type"], "null")

    def test_feed_schema_requires_full_commit_sha(self):
        schema = json.loads((BASE / "schemas" / "feed-envelope.schema.json").read_text(encoding="utf-8"))
        revision = schema["properties"]["revision"]
        self.assertEqual(revision["pattern"], "^[a-f0-9]{40}$")
        self.assertEqual(revision["minLength"], 40)
        self.assertEqual(revision["maxLength"], 40)
        self.assertTrue(re.fullmatch(revision["pattern"], "a" * 40))
        self.assertFalse(re.fullmatch(revision["pattern"], "a" * 40 + "\\n"))

    def test_validator_rejects_unknown_mapping_capability(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            fixture = root / "docs" / "integrations" / "polyglot"
            shutil.copytree(BASE, fixture)
            mapping_path = fixture / "examples" / "mapping-quic-streams.json"
            mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
            mapping["capability_id"] = "missing.capability"
            mapping_path.write_text(json.dumps(mapping), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "polyglot" / "validate_federation.py"), "--root", str(root)],
                capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("capability_id does not resolve", result.stderr)

    def test_validator_passes(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "polyglot" / "validate_federation.py")],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

if __name__ == "__main__":
    unittest.main()
