from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "import_claude_export", ROOT / "scripts/skills/import_claude_export.py"
)
IMPORTER = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(IMPORTER)


class ClaudeExportImportTests(unittest.TestCase):
    def test_missing_jsonl_is_derived_from_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            csv_path = root / "skills-inventory.csv"
            jsonl_path = root / "skills-inventory.jsonl"
            fields = ["namespace", "plugin_dir", "skill_path", "name", "description", "bytes", "sha1"]
            with csv_path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                writer.writerow({
                    "namespace": "examples",
                    "plugin_dir": "",
                    "skill_path": "examples/demo/SKILL.md",
                    "name": "demo",
                    "description": "fixture",
                    "bytes": "10",
                    "sha1": "0123456789ab",
                })
            returned_fields, rows, jsonl_rows, origin = IMPORTER.load_skill_inventory(
                csv_path, jsonl_path
            )
        self.assertEqual(returned_fields, fields)
        self.assertEqual(jsonl_rows, rows)
        self.assertEqual(origin, "derived-from-skills-inventory.csv")

    def test_downloaded_jsonl_must_match_csv_field_for_field(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            csv_path = root / "skills-inventory.csv"
            jsonl_path = root / "skills-inventory.jsonl"
            fields = ["namespace", "plugin_dir", "skill_path", "name", "description", "bytes", "sha1"]
            with csv_path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                writer.writerow({
                    "namespace": "examples", "plugin_dir": "",
                    "skill_path": "examples/demo/SKILL.md", "name": "demo",
                    "description": "fixture", "bytes": "10", "sha1": "0123456789ab",
                })
            jsonl_path.write_text(json.dumps({
                "namespace": "wrong", "plugin_dir": "",
                "skill_path": "examples/demo/SKILL.md", "name": "demo",
                "description": "fixture", "bytes": 10, "sha1": "0123456789ab",
            }) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "record mismatch"):
                IMPORTER.load_skill_inventory(csv_path, jsonl_path)

    def test_checksum_coverage_reports_unverified_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            part = root / "skills-part-00.tgzpart"
            part.write_bytes(b"verified fixture payload")
            expected = hashlib.sha256(part.read_bytes()).hexdigest()
            sums = root / "SHA256SUMS.txt"
            sums.write_text(f"{expected}  {part.name}\n", encoding="utf-8")
            inputs = tuple(root / name for name in (
                "skills-SKILL-md-all.tar.gz",
                "skills-inventory.csv",
                "plugins-inventory.csv",
            ))
            result = IMPORTER.verify_checksum_coverage(root, sums, inputs)
        self.assertEqual(result["status"], "UNVERIFIED")
        self.assertEqual(result["verified_files"], [part.name])
        self.assertEqual(result["unchecksummed_inputs"], sorted(p.name for p in inputs))

    def test_checksum_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            part = root / "skills-part-00.tgzpart"
            part.write_bytes(b"changed payload")
            sums = root / "SHA256SUMS.txt"
            sums.write_text(f'{"0" * 64}  {part.name}\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                IMPORTER.verify_checksum_coverage(root, sums, (part,))

    def test_checksum_path_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            sums = Path(tmp) / "SHA256SUMS.txt"
            sums.write_text(f'{"a" * 64}  ../outside.tgzpart\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Unsafe checksum filename"):
                IMPORTER.parse_sha256sums(sums)


if __name__ == "__main__":
    unittest.main()
