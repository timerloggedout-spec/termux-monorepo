import unittest

from scripts.agent_evolution.action_effect_importer import history_from_action_effect_state


class ActionEffectImporterTests(unittest.TestCase):
    def test_preserves_event_identity_and_temporal_fields(self):
        history = history_from_action_effect_state({
            "recent_events": [
                {"id": "review-1", "at": "2026-09-22T12:00:00Z",
                 "associated_commit_sha": "a" * 40, "lag_minutes": 7,
                 "relationship": "FOLLOWED_BY_COMMIT"},
                {"id": "comment-2", "at": "2026-09-22T12:02:00Z",
                 "associated_commit_sha": None, "lag_minutes": None,
                 "relationship": "NO_LATER_COMMIT_IN_RANGE"},
            ]
        })
        self.assertEqual([n.node_id for n in history.nodes],
                         ["action-effect:review-1", "action-effect:comment-2"])
        self.assertEqual(history.nodes[0].score, 1.0)
        self.assertEqual(history.nodes[0].cost, 7.0)
        self.assertEqual(history.nodes[1].score, 0.0)

    def test_rejects_invalid_relationship(self):
        with self.assertRaises(ValueError):
            history_from_action_effect_state({"recent_events": [{
                "id": "bad", "at": "2026-09-22T12:00:00Z",
                "relationship": "CAUSED_BY",
            }]})

    def test_empty_bounded_window_is_valid(self):
        self.assertEqual(history_from_action_effect_state({"recent_events": []}).nodes, ())


if __name__ == "__main__":
    unittest.main()