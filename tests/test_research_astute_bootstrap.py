from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ResearchAstuteBootstrapTests(unittest.TestCase):
    def test_bootstrap_targets_verified_owner_and_explicit_creation_gate(self) -> None:
        workflow = (ROOT / ".github/workflows/research-astute-organization-bootstrap.yml").read_text(encoding="utf-8")
        self.assertIn("TARGET_ORG: Research-Astute", workflow)
        self.assertIn("provision_missing", workflow)
        self.assertIn("default: false", workflow)
        self.assertIn('if [[ "$PROVISION_MISSING" == "true" ]]', workflow)
        self.assertIn("RESEARCH_ASTUTE_GITHUB_TOKEN", workflow)
        self.assertIn('-F "private=true"', workflow)

    def test_collection_registry_uses_verified_owner_and_five_repositories(self) -> None:
        registry = json.loads((ROOT / "docs/research-astute/registry/collections.json").read_text(encoding="utf-8"))
        repositories = [item["repository"] for item in registry["collections"]]
        self.assertEqual(registry["domain_controller"], "Research-Astute")
        self.assertEqual(
            repositories,
            [
                "Research-Astute/research-astute-space-systems",
                "Research-Astute/research-astute-nasa-missions",
                "Research-Astute/research-astute-tesla-mobility-energy",
                "Research-Astute/research-astute-aerospace-energy-patents",
                "Research-Astute/research-astute-foss-research",
            ],
        )


if __name__ == "__main__":
    unittest.main()
