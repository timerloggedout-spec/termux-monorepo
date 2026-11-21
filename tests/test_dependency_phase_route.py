from __future__ import annotations

import unittest
from unittest.mock import patch

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "agentic"))

from dependency_phase_route import resolve_route  # noqa: E402


ROSTER = (ROOT / "docs" / "schemas" / "agent-roster.yaml").read_text(encoding="utf-8")


def plan(preferred_agent=None):
    execution = {"mode": "agent", "capability": "build"}
    if preferred_agent:
        execution["preferred_agent"] = preferred_agent
    return {
        "policy": {"dispatch_agents": ["tembo", "mistral_vibe", "gemini", "openrouter", "grok"]},
        "phases": [{
            "phase_id": "DPH-100",
            "execution": execution,
        }],
    }


class DependencyPhaseRouteTests(unittest.TestCase):
    def test_candidate_pool_schema_is_read_from_agent_roster(self):
        with patch.dict("os.environ", {"ROUTE_TEMBO_ADAPTER_READY": "true"}, clear=True):
            result = resolve_route(plan(), "DPH-100", ROSTER)
        self.assertEqual(["tembo", "mistral_vibe", "gemini", "openrouter"], result["candidates"])
        self.assertEqual("tembo", result["selected_specialist"])

    def test_explicit_preference_wins_only_when_available(self):
        with patch.dict(
            "os.environ",
            {"ROUTE_MISTRAL_VIBE_ADAPTER_READY": "true", "ROUTE_TEMBO_ADAPTER_READY": "true"},
            clear=True,
        ):
            result = resolve_route(plan("mistral_vibe"), "DPH-100", ROSTER)
        self.assertEqual("mistral_vibe", result["selected_specialist"])
        self.assertEqual("routed", result["state"])

    def test_multiple_available_specialists_require_manager_selection(self):
        with patch.dict(
            "os.environ",
            {"ROUTE_TEMBO_ADAPTER_READY": "true", "ROUTE_GEMINI_ADAPTER_READY": "true"},
            clear=True,
        ):
            result = resolve_route(plan(), "DPH-100", ROSTER)
        self.assertEqual("manager_selection_required", result["state"])
        self.assertIsNone(result["selected_specialist"])
        self.assertEqual(["tembo", "gemini"], result["available_candidates"])

    def test_manager_can_select_one_of_multiple_live_specialists(self):
        with patch.dict(
            "os.environ",
            {"ROUTE_TEMBO_ADAPTER_READY": "true", "ROUTE_GEMINI_ADAPTER_READY": "true"},
            clear=True,
        ):
            result = resolve_route(
                plan(),
                "DPH-100",
                ROSTER,
                selected_specialist="gemini",
            )
        self.assertEqual("routed", result["state"])
        self.assertEqual("gemini", result["selected_specialist"])

    def test_manager_selection_must_be_live_and_approved(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "outside the live manager-approved candidate set"):
                resolve_route(plan(), "DPH-100", ROSTER, selected_specialist="jules")

    def test_no_available_adapter_stops_without_claiming_a_specialist(self):
        with patch.dict("os.environ", {}, clear=True):
            result = resolve_route(plan(), "DPH-100", ROSTER)
        self.assertEqual("no_available_specialist", result["state"])
        self.assertIsNone(result["selected_specialist"])

    def test_retired_jules_is_not_a_candidate_or_implicit_fallback(self):
        with patch.dict("os.environ", {"ROUTE_JULES_ADAPTER_READY": "true"}, clear=True):
            result = resolve_route(plan(), "DPH-100", ROSTER)
        self.assertNotIn("jules", result["candidates"])
        self.assertNotIn("jules", result["available_candidates"])
        self.assertIsNone(result["selected_specialist"])


if __name__ == "__main__":
    unittest.main()
