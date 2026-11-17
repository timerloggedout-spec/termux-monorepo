import unittest
from unittest.mock import patch

from scripts.ops import provider_invoke


def population():
    return {
        "schema": "orbit-provider-population/v1",
        "provider_count": 1,
        "inference_wiring": {"wired": 1, "total": 1},
        "endpoint_census": {"verified_floor": 7341},
        "g4f": {
            "universe_providers": 160,
            "universe_pairs": 9588,
            "sandbox_verified_pairs": 160,
            "actions_verified_pairs": 83,
        },
        "providers": [{
            "id": "alpha",
            "availability_record_count": 1,
            "invoke_route_registered": True,
        }],
    }


class ProviderInvokeControlPlaneTests(unittest.TestCase):
    @patch("scripts.orbit_provider_population.load_population", return_value=population())
    def test_observation_is_advisory_and_does_not_echo_prompt(self, _load):
        prompt = "private task prompt that must not appear in telemetry"
        observation = provider_invoke.control_plane_observation(prompt)

        self.assertEqual(observation["mode"], "observe_only")
        self.assertEqual(observation["status"], "observed")
        self.assertEqual(observation["population"]["provider_count"], 1)
        self.assertEqual(observation["population"]["g4f_actions_verified_pairs"], 83)
        self.assertEqual(observation["orbit"]["decision"], "DEFER")
        self.assertEqual(observation["shield"]["counts"]["quarantine"], 1)
        self.assertEqual(observation["shield"]["signals"][0]["disposition"], "quarantine")
        self.assertNotIn(prompt, str(observation))
        self.assertNotIn("content", str(observation))

    @patch("scripts.orbit_provider_population.load_population", return_value=population())
    def test_catalog_only_observation_has_empty_context_capsule(self, _load):
        observation = provider_invoke.control_plane_observation()
        self.assertEqual(observation["status"], "observed")
        self.assertEqual(observation["shield"]["counts"]["admit"], 0)
        self.assertEqual(observation["shield"]["counts"]["quarantine"], 0)

    @patch("scripts.orbit_provider_population.load_population", side_effect=OSError("private path detail"))
    def test_observation_failure_does_not_escape_or_break_invoke(self, _load):
        observation = provider_invoke.control_plane_observation("private prompt")
        self.assertEqual(observation, {
            "mode": "observe_only",
            "status": "unavailable",
            "error_class": "OSError",
        })
        self.assertNotIn("private path detail", str(observation))


if __name__ == "__main__":
    unittest.main()
