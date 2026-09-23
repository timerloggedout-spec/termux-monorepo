import json
import unittest
from datetime import date
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "agentic"))

from gantt_projection import project, render_mermaid_gantt

PLAN = json.loads((ROOT / "docs" / "agentic" / "dependency-phases.json").read_text(encoding="utf-8"))
REPORT = json.loads((ROOT / "docs" / "agentic" / "dependency-phase-report.json").read_text(encoding="utf-8"))


class GanttProjectionTests(unittest.TestCase):
    def test_relative_projection_preserves_stable_ids_dependencies_and_critical_path(self):
        result = project(PLAN)
        self.assertEqual(result["projection"], "gantt.interchange.v1")
        self.assertEqual(result["schedule_mode"], "relative-wave")
        self.assertEqual([t["id"] for t in result["tasks"]], ["DPH-000", "DPH-100", "DPH-200", "DPH-300"])
        self.assertEqual(result["tasks"][1]["dependencies"], ["DPH-000"])
        self.assertEqual(result["tasks"][2]["wave"], 2)
        self.assertTrue(all(task["critical"] for task in result["tasks"]))

    def test_date_projection_is_deterministic_and_marks_critical_path(self):
        result = project(PLAN, start_date=date(2026, 9, 22), default_duration_days=1)
        self.assertEqual(result["tasks"][0]["start"], "2026-09-22")
        self.assertEqual(result["tasks"][3]["end"], "2026-09-25")
        self.assertTrue(all(task["critical"] for task in result["tasks"]))

    def test_duration_mapping_changes_schedule_without_mutating_plan(self):
        before = json.dumps(PLAN, sort_keys=True)
        result = project(PLAN, start_date=date(2026, 9, 22), default_duration_days=1, duration_mapping={"DPH-100": 3})
        self.assertEqual(before, json.dumps(PLAN, sort_keys=True))
        self.assertEqual(result["tasks"][2]["start"], "2026-09-26")

    def test_mermaid_projection_is_derived(self):
        result = project(PLAN, start_date=date(2026, 9, 22))
        text = render_mermaid_gantt(result)
        self.assertIn("gantt", text)
        self.assertIn("DPH_000", text)
        self.assertIn("crit", text)

    def test_mermaid_collapses_title_whitespace(self):
        phases = [{**phase} for phase in PLAN["phases"]]
        phases[0] = {**phases[0], "title": "line one\nline two"}
        result = project({**PLAN, "phases": phases}, start_date=date(2026, 9, 22))
        self.assertIn("line one line two", render_mermaid_gantt(result))

    def test_valid_report_projects_evaluation_state(self):
        result = project(PLAN, report=REPORT)
        self.assertEqual(result["tasks"][0]["state"], "complete")
        self.assertEqual(result["tasks"][1]["state"], "ready")

    def test_malformed_report_fails_closed(self):
        for malformed in (
            {"evaluations": {}},
            {"evaluations": [dict(REPORT["evaluations"][0], phase_id="NOT-A-PHASE")]},
            {"evaluations": [dict(REPORT["evaluations"][0], pull_requests="900")]},
        ):
            with self.assertRaises(ValueError):
                project(PLAN, report=malformed)

    def test_incomplete_report_fails_closed(self):
        malformed = dict(REPORT)
        malformed["evaluations"] = REPORT["evaluations"][:-1]
        with self.assertRaises(ValueError):
            project(PLAN, report=malformed)

    def test_unknown_duration_id_fails_closed(self):
        with self.assertRaises(ValueError):
            project(PLAN, duration_mapping={"NOT-A-PHASE": 2})


if __name__ == "__main__":
    unittest.main()
