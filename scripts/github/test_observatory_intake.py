#!/usr/bin/env python3
import sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.github import observatory_intake as oi

SERVICE_FORM = """### Service ID

gravitee-api-management

### Service Name

Gravitee API Management

### Upstream repository

gravitee-io/gravitee-api-management

### Observatory signal

starred

### Category

api-management
"""

def issue(n, labels, body, pr=False):
    d = {"number": n, "labels": [{"name": x} for x in labels], "body": body,
         "created_at": "2026-10-28T00:00:00Z"}
    if pr:
        d["pull_request"] = {"url": "x"}
    return d

class IntakeTests(unittest.TestCase):
    def test_collect_maps_template_issue(self):
        doc = oi.collect([issue(2059, ["research", "research:service"], SERVICE_FORM)])
        self.assertEqual(doc["schema_version"], "observatory-intake/v1")
        self.assertEqual(len(doc["entries"]), 1)
        e = doc["entries"][0]
        self.assertEqual(e["upstream"], "gravitee-io/gravitee-api-management")
        self.assertEqual(e["signal"], "starred")
        self.assertEqual(e["seed_id"], "github:research-seed:gravitee-io/gravitee-api-management")

    def test_dedupe_skip_and_pr_excluded(self):
        doc = oi.collect([
            issue(1, ["research:service"], SERVICE_FORM),
            issue(1, ["research:service"], SERVICE_FORM),          # duplicate fetch via 2nd label query shape
            issue(2, ["research:provider"], "not a form"),          # unparseable -> skipped
            issue(3, ["research:service"], SERVICE_FORM, pr=True), # PR, not an issue filing
            issue(4, ["bug"], SERVICE_FORM),                        # unlabeled for research
        ])
        self.assertEqual([e["issue"] for e in doc["entries"]], [1])
        self.assertEqual(doc["skipped_unparseable"], 1)

if __name__ == "__main__":
    unittest.main()
