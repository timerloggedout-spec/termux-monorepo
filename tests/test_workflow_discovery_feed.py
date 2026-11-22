"""Tests for nested Actions workflow discovery and evidence joins."""
from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.dashboards.workflow_discovery_feed import build_feed


class WorkflowDiscoveryFeedTests(unittest.TestCase):
    def test_nested_edges_and_observed_metrics(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "upstream.yml").write_text(
                "name: Upstream\non:\n  push:\njobs:\n  build:\n    runs-on: ubuntu-latest\n",
                encoding="utf-8",
            )
            (root / "downstream.yml").write_text(
                "name: Downstream\non:\n  workflow_run:\n    workflows:\n      - Upstream\n    types: [completed]\njobs:\n  aggregate:\n    needs: [prep, build]\n    uses: ./.github/workflows/reusable.yml\n  prep:\n    runs-on: ubuntu-latest\n  build:\n    runs-on: ubuntu-latest\n",
                encoding="utf-8",
            )
            (root / "reusable.yml").write_text(
                "name: Reusable\non:\n  workflow_call:\njobs:\n  run:\n    runs-on: ubuntu-latest\n",
                encoding="utf-8",
            )
            catalog = {
                "source_fingerprint": "abc",
                "workflows": [
                    {"path": ".github/workflows/upstream.yml", "name": "Upstream",
                     "domain": "validation", "authority": "read-only",
                     "triggers": ["push"], "schedules": [], "jobs": ["build"]},
                    {"path": ".github/workflows/downstream.yml", "name": "Downstream",
                     "domain": "ops", "authority": "writer",
                     "triggers": ["workflow_run"], "schedules": [],
                     "jobs": ["aggregate", "prep", "build"]},
                    {"path": ".github/workflows/reusable.yml", "name": "Reusable",
                     "domain": "ops", "authority": "read-only",
                     "triggers": ["workflow_call"], "schedules": [],
                     "jobs": ["run"]},
                ],
            }
            observations = {
                "read_at": "2026-11-22T00:00:00Z",
                "budget": {"calls_made": 3, "pages_sampled": [1, 2, 3]},
                "totals": {"runs": 2, "workflows": 1},
                "workflows": {
                    ".github/workflows/upstream.yml": {
                        "runs": 2, "concluded": 2, "failures": 1,
                        "failure_rate": 0.5, "duration_excluded": 0,
                        "events": {"push": 2},
                        "red": {"sample_rate_per_hour": 2.0,
                                "duration_s": {"n": 2, "median": 60, "p95": 90, "mean": 70}},
                        "latest": {"id": 10},
                    }
                },
            }
            feed = build_feed(
                catalog, observations, workflow_root=root,
                generated_at="2026-11-22T00:00:00Z",
            )
            self.assertEqual(feed["summary"]["workflow_definitions"], 3)
            self.assertEqual(feed["summary"]["observed_workflows"], 1)
            self.assertEqual(feed["summary"]["workflow_run_edges"], 1)
            self.assertEqual(feed["summary"]["reusable_workflow_edges"], 1)
            self.assertEqual(feed["summary"]["job_dependency_edges"], 2)
            self.assertEqual(
                feed["edges"][0],
                {"from": ".github/workflows/upstream.yml",
                 "to": ".github/workflows/downstream.yml",
                 "kind": "workflow_run", "source_name": "Upstream"},
            )
            self.assertEqual(
                feed["edges"][1],
                {"from": ".github/workflows/downstream.yml",
                 "to": ".github/workflows/reusable.yml",
                 "kind": "reusable_workflow"},
            )
            observed = feed["workflows"][2]["run_observation"]
            self.assertEqual(observed["failure_rate"], 0.5)
            self.assertEqual(feed["summary"]["observation_state"], "fresh")

    def test_unresolved_reference_and_stale_observation_are_explicit(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "downstream.yml").write_text(
                "name: Downstream\non:\n  workflow_run:\n    workflows: [Missing Workflow]\njobs:\n  run:\n    runs-on: ubuntu-latest\n",
                encoding="utf-8",
            )
            catalog = {
                "workflows": [
                    {"path": ".github/workflows/downstream.yml", "name": "Downstream",
                     "triggers": ["workflow_run"], "jobs": ["run"]},
                ]
            }
            observations = {
                "read_at": "2026-11-19T00:00:00Z",
                "totals": {"runs": 0, "workflows": 0},
                "workflows": {},
            }
            feed = build_feed(
                catalog, observations, workflow_root=root,
                generated_at="2026-11-22T00:00:00Z",
            )
            self.assertEqual(feed["summary"]["observation_state"], "stale")
            self.assertEqual(feed["unresolved_references"][0]["reference"], "Missing Workflow")
            self.assertTrue(any("stale" in gap for gap in feed["gaps"]))
            self.assertTrue(any("unresolved" in gap for gap in feed["gaps"]))
            self.assertEqual(feed["workflows"][0]["run_observation"]["state"], "unobserved")

    def test_missing_observation_is_unknown_not_zero(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog = {"workflows": [
                {"path": ".github/workflows/a.yml", "name": "A", "triggers": [], "jobs": []}
            ]}
            feed = build_feed(catalog, None, workflow_root=root,
                              generated_at="2026-11-22T00:00:00Z")
            self.assertEqual(feed["workflows"][0]["run_observation"], {"state": "unobserved"})
            self.assertEqual(feed["summary"]["observation_state"], "stale")
            self.assertTrue(any("UNKNOWN" in gap for gap in feed["gaps"]))


if __name__ == "__main__":
    unittest.main()
