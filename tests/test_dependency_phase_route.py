from __future__ import annotations

import unittest
from unittest.mock import patch

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "agentic"))

from dependency_phase_route import resolve_route  # noqa: E402


ROSTER = """
routing:
  build:
    primary: jules
    fallback: [tembo, mistral_vibe]
  fix:
    primary: jules
    fallback: [tembo, grok]
"""


def plan():
    return {
        "policy": {"dispatch_agents": ["jules", "tembo", "mistral_vibe"]},
        "phases": [{
            "phase_id": "DPH-100",
            "execution": {
                "mode": "agent",
                "capability": "build",
                "preferred_agent": "jules",
            },
        }],
    }


class DependencyPhaseRouteTests(unittest.TestCase):
    def test_preferred_specialist_is_selected_only_when_available(self):
        with patch.dict("os.environ", {"ROUTE_JULES_ADAPTER_READY": "true"}, clear=False):
            result = resolve_route(plan(), "DPH-100", ROSTER)
        self.assertEqual("routed", result["state"])
        self.assertEqual("jules", result["selected_specialist"])
        self.assertEqual(["jules", "tembo", "mistral_vibe"], result["candidates"])

    def test_manager_router_uses_roster_fallback_without_invoking_it(self):
        with patch.dict(
            "os.environ",
            {"ROUTE_JULES_ADAPTER_READY": "false", "ROUTE_TEMBO_ADAPTER_READY": "true"},
            clear=False,
        ):
            result = resolve_route(plan(), "DPH-100", ROSTER)
        self.assertEqual("tembo", result["selected_specialist"])
        self.assertEqual("agent-roster-routing-v1", result["manager_policy"])

    def test_missing_adapter_does_not_fall_through_to_direct_jules(self):
        with patch.dict(
            "os.environ",
            {"ROUTE_JULES_ADAPTER_READY": "false", "ROUTE_TEMBO_ADAPTER_READY": "false"},
            clear=False,
        ):
            result = resolve_route(plan(), "DPH-100", ROSTER)
        self.assertEqual("no_available_specialist", result["state"])
        self.assertIsNone(result["selected_specialist"])


if __name__ == "__main__":
    unittest.main()
