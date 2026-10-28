import json, subprocess, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.research import research_intake as ri

PROVIDER_FORM = """### Provider ID

acme-ai

### Provider Name

Acme AI

### Category

model

### Website / Docs URL

https://acme.example/docs

### Free Quota

1000 req/day — https://acme.example/pricing

### Auth from Actions

ACME_API_KEY

### Evidence and sources

https://acme.example/pricing
"""

SERVICE_CMD = """<!-- request-research -->
kind: service
id: gravitee
name: Gravitee API Management
upstream: gravitee-io/gravitee-api-management
signal: starred
category: api-management
"""


class ResearchIntakeTests(unittest.TestCase):
    def test_provider_form_maps_to_seed(self):
        rec = ri.build_record("provider", ri.parse_form(PROVIDER_FORM))
        self.assertEqual(rec["seed_id"], "research-seed:provider:acme-ai")
        self.assertEqual(rec["observed_facts"]["auth_secret_name"], "ACME_API_KEY")
        self.assertIn("provider-recon-compound", rec["starter"]["pipeline"])
        self.assertEqual(rec["classification"]["adoption"], "research-only")

    def test_service_command_seed_matches_research_seeds_schema(self):
        rec = ri.build_record("service", ri.parse_command(SERVICE_CMD))
        self.assertEqual(rec["seed_id"],
                         "github:research-seed:gravitee-io/gravitee-api-management")
        self.assertIn("observatory-signal:starred", rec["provenance"])
        for key in ("schema_version", "seed_id", "canonical_upstream",
                    "provenance", "classification", "observed_facts",
                    "capability_signals", "integration_constraints"):
            self.assertIn(key, rec)

    def test_secret_value_refused(self):
        f = ri.parse_form(PROVIDER_FORM)
        f["auth"] = "ghp_" + "a" * 30
        with self.assertRaises(ValueError):
            ri.build_record("provider", f)

    def test_bad_signal_and_missing_id_refused(self):
        with self.assertRaises(ValueError):
            ri.build_record("service", {"id": "x", "name": "X", "signal": "viral"})
        with self.assertRaises(ValueError):
            ri.build_record("provider", {"name": "X"})

    def test_cli_markdown(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as t:
            t.write(SERVICE_CMD); path = t.name
        out = subprocess.run([sys.executable, "-m", "scripts.research.research_intake",
                              path, "--markdown"], capture_output=True, text=True,
                             cwd=Path(__file__).resolve().parents[1])
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("repository-observatory", out.stdout)
        json.loads(out.stdout.split("```json")[1].split("```")[0])


if __name__ == "__main__":
    unittest.main()
