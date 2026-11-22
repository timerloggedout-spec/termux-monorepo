from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "scripts/ci/build_architecture_portal.py"
SPEC = importlib.util.spec_from_file_location("build_architecture_portal", MODULE)
portal = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(portal)


class ArchitecturePortalBuilderTests(unittest.TestCase):
    def make_repo(self, root: Path) -> None:
        files = {
            "architecture.md": "# Repository Architecture\n\nCanonical root map.\n",
            "docs/architecture/README.md": "# Architecture Index\n\nDomain index.\n",
            "docs/architecture/flows/execution-session.md": "# Execution and Session\n\nFlow notes.\n",
            "docs/architecture/flows/execution-session.mmd": "flowchart LR\n A-->B\n",
            "docs/architecture/flows/fenced.mmd": "```mermaid\nflowchart TD\n A-->B\n```\n\nA Markdown-wrapped Mermaid source.\n",
            "docs/architecture/flows/imported.svg": "<svg xmlns=\"http://www.w3.org/2000/svg\"><title>Imported</title></svg>\n",
            "docs/ops/diagrams/repository-data-flow.mmd": "flowchart TB\n A-->C\n",
            "docs/ops/generated/legacy.svg": "<svg xmlns=\"http://www.w3.org/2000/svg\"><title>Legacy</title></svg>\n",
            "docs/ops/generated/preview.png": "png-bytes",
            "docs/agentic/dependency-phases.mmd": "flowchart TD\n A-->B\n",
            "docs/assets/ates-attention-placeholder.svg": "<svg xmlns=\"http://www.w3.org/2000/svg\"><title>ATES</title></svg>\n",
            "docs/ops/SHE-DASHBOARD-INDEX.md": "# SHE Dashboard Index\n\nArchitecture navigation.\n",
            "docs/unrelated/private-notes.md": "# Excluded\n\nOutside the architecture scope.\n",
        }
        for name, content in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

    def test_builds_scoped_catalog_copies_sources_and_records_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            output = Path(tmp) / "site" / "architecture"
            root.mkdir()
            self.make_repo(root)

            catalog = portal.build_portal(root, output, "master", "abc123")
            by_path = {item["path"]: item for item in catalog["items"]}

            self.assertIn("architecture.md", by_path)
            self.assertIn("docs/architecture/flows/execution-session.mmd", by_path)
            self.assertIn("docs/architecture/flows/fenced.mmd", by_path)
            self.assertIn("docs/architecture/flows/imported.svg", by_path)
            self.assertIn("docs/ops/diagrams/repository-data-flow.mmd", by_path)
            self.assertIn("docs/agentic/dependency-phases.mmd", by_path)
            self.assertIn("docs/assets/ates-attention-placeholder.svg", by_path)
            self.assertIn("docs/ops/SHE-DASHBOARD-INDEX.md", by_path)
            self.assertNotIn("docs/unrelated/private-notes.md", by_path)

            diagram = by_path["docs/architecture/flows/execution-session.mmd"]
            self.assertEqual(diagram["kind"], "mermaid")
            self.assertEqual(diagram["render_path"], "assets/diagrams/docs/architecture/flows/execution-session.svg")
            fenced = by_path["docs/architecture/flows/fenced.mmd"]
            render_input = output / fenced["render_input_path"]
            self.assertIn("flowchart TD", render_input.read_text(encoding="utf-8"))
            self.assertNotIn("```", render_input.read_text(encoding="utf-8"))
            self.assertEqual(diagram["source_ref"], "master")
            self.assertEqual(len(diagram["sha256"]), 64)
            self.assertTrue((output / diagram["site_path"]).is_file())

            svg = by_path["docs/architecture/flows/imported.svg"]
            self.assertEqual(svg["kind"], "svg")
            self.assertTrue((output / svg["asset_path"]).is_file())
            self.assertEqual(catalog["source_sha"], "abc123")
            self.assertTrue(catalog["generated_at"].endswith("Z"))
            self.assertEqual(json.loads((output / "catalog.json").read_text())["items"], catalog["items"])

    def test_allows_output_inside_repository_site_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            self.make_repo(root)
            output = root / "_site/architecture"

            catalog = portal.build_portal(root, output, "master", "abc123")

            self.assertTrue((output / "catalog.json").is_file())
            self.assertGreater(catalog["item_count"], 0)

    def test_verification_requires_each_mermaid_svg_render(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            output = Path(tmp) / "site" / "architecture"
            root.mkdir()
            self.make_repo(root)
            portal.build_portal(root, output, "master", "abc123")

            missing = portal.verify_rendered(output)
            self.assertEqual(len(missing), 4)
            for item in json.loads((output / "catalog.json").read_text())["items"]:
                if item["kind"] == "mermaid":
                    render = output / item["render_path"]
                    render.parent.mkdir(parents=True, exist_ok=True)
                    render.write_text("<svg xmlns=\"http://www.w3.org/2000/svg\"></svg>", encoding="utf-8")
            self.assertEqual(portal.verify_rendered(output), [])

    def test_finalize_removes_internal_render_inputs_from_published_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            output = Path(tmp) / "site" / "architecture"
            root.mkdir()
            self.make_repo(root)
            portal.build_portal(root, output, "master", "abc123")
            for item in json.loads((output / "catalog.json").read_text())["items"]:
                if item["kind"] == "mermaid":
                    render = output / item["render_path"]
                    render.parent.mkdir(parents=True, exist_ok=True)
                    render.write_text("<svg xmlns=\"http://www.w3.org/2000/svg\"></svg>", encoding="utf-8")

            portal.finalize_bundle(output)
            catalog = json.loads((output / "catalog.json").read_text())

            self.assertFalse((output / "render-inputs").exists())
            self.assertTrue(all("render_input_path" not in item for item in catalog["items"]))
            self.assertTrue(all((output / item["render_path"]).is_file() for item in catalog["items"] if item["kind"] == "mermaid"))

    def test_rejects_symlink_that_escapes_repository_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            output = Path(tmp) / "site"
            root.mkdir()
            (root / "docs/architecture").mkdir(parents=True)
            outside = Path(tmp) / "outside.md"
            outside.write_text("# Outside\n", encoding="utf-8")
            (root / "docs/architecture/escape.md").symlink_to(outside)
            with self.assertRaises(ValueError):
                portal.build_portal(root, output, "master", "abc123")


if __name__ == "__main__":
    unittest.main()
