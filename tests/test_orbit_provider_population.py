import unittest
from pathlib import Path

from scripts import orbit_provider_population as population


class OrbitProviderPopulationTests(unittest.TestCase):
    def test_build_population_deduplicates_provider_names_and_keeps_evidence_classes(self):
        feed = {
            "schema": "desk-feed/v1.3",
            "dispatch": {
                "provider_catalog": {
                    "inference_availability": {
                        "records": [
                            {"id": "alpha.chat", "provider": "alpha", "class": "proven", "invoke_verdict": "INVOKE OK"},
                            {"id": "alpha.embed", "provider": "alpha", "class": "proven"},
                            {"id": "beta.chat", "provider": "beta", "class": "wired-unproven"},
                        ]
                    },
                    "inference_only": {"distinct_providers": ["alpha", "beta", "g4f/Gemini"]},
                    "inference_wiring": {
                        "wired_invoke": {
                            "count": 2,
                            "of": 3,
                            "named_providers": ["alpha"],
                            "by_surface": {
                                "g4f-working/gpt4free route": {
                                    "actions_verified": {
                                        "inference_ok": 1,
                                        "attempted": 2,
                                        "providers_ok": {"Gemini": 1},
                                    }
                                }
                            },
                        }
                    },
                    "compounding": {
                        "g4f_verified_pool": {
                            "inference_ok_pairs": 160,
                            "of_universe_pairs": 9588,
                            "actions_verified": {
                                "inference_ok": 83,
                                "attempted": 160,
                                "run": 41457191473,
                                "artifact": 13154370032,
                                "providers_ok": {"Gemini": 18, "AnyProvider": 29},
                            },
                        }
                    },
                    "endpoint_census": {"verified_floor": 7341, "counted_at": "2026-11-01"},
                }
            },
        }
        working = {
            "schema": "g4f-working-endpoints/v1",
            "universe": {"providers_total": 160, "pairs_total": 9588},
            "attempted": 2,
            "inference_ok": 2,
            "endpoints": [
                {"provider": "Gemini", "model": "gemini-2.5-flash"},
                {"provider": "Gemini", "model": "gemini-2.5-pro"},
            ],
        }

        result = population.build_population(feed, working)
        self.assertEqual(result["provider_count"], 3)
        self.assertEqual(result["inference_wiring"], {"wired": 2, "total": 3})
        self.assertEqual(result["endpoint_census"]["verified_floor"], 7341)
        gemini = next(item for item in result["providers"] if item["id"] == "g4f/Gemini")
        self.assertEqual(gemini["g4f_sandbox_verified_pairs"], 2)
        self.assertTrue(gemini["invoke_route_registered"])
        self.assertEqual(result["g4f"]["sandbox_verified_pairs"], 160)
        self.assertEqual(result["g4f"]["actions_verified_pairs"], 83)
        self.assertEqual(result["g4f"]["actions_verified_attempted_pairs"], 160)
        self.assertEqual(result["g4f"]["actions_verified_run_id"], 41457191473)
        self.assertEqual(result["g4f"]["actions_verified_artifact_id"], 13154370032)
        self.assertEqual(result["g4f"]["actions_verified_provider_count"], 2)
        alpha = next(item for item in result["providers"] if item["id"] == "alpha")
        self.assertEqual(alpha["dispatch_classes"], ["proven"])
        self.assertEqual(alpha["availability_record_count"], 2)

    def test_orbit_candidates_preserve_unknowns_instead_of_inventing_scores(self):
        feed = {
            "schema": "desk-feed/v1.3",
            "dispatch": {
                "provider_catalog": {
                    "inference_availability": {"records": [{"id": "alpha.chat", "provider": "alpha", "class": "proven"}]},
                    "inference_only": {"distinct_providers": ["alpha"]},
                    "inference_wiring": {"wired_invoke": {"count": 1, "of": 1, "named_providers": ["alpha"]}},
                    "endpoint_census": {"verified_floor": 1, "counted_at": "2026-11-01"},
                }
            },
        }
        result = population.build_population(feed)
        candidates = population.as_orbit_candidates(result)
        self.assertEqual(len(candidates), 1)
        self.assertIsNone(candidates[0]["benefit"]["repository_outcome"])
        self.assertIsNone(candidates[0]["risk_cost"]["failure_risk"])
        self.assertIsNone(candidates[0]["hard_gates"]["authentication"])

    def test_live_dispatch_population_exposes_full_registered_provider_universe(self):
        root = Path(__file__).resolve().parents[1]
        result = population.load_population(root)
        self.assertGreaterEqual(result["provider_count"], 90)
        self.assertGreaterEqual(result["endpoint_census"]["verified_floor"], 7000)
        self.assertGreaterEqual(result["inference_wiring"]["wired"], 90)
        candidates = population.as_orbit_candidates(result)
        self.assertEqual(len(candidates), result["provider_count"])
        self.assertTrue(all(item["identity"]["kind"] == "provider_route" for item in candidates))


if __name__ == "__main__":
    unittest.main()
