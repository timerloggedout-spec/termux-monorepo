import json
import unittest
from unittest.mock import patch, MagicMock
from scripts.live_catalog_feed import (
    _is_free,
    _token,
    poll_provider,
    load_eligible,
    peer_candidates_for_role,
    SPECIAL_FREE_MODELS,
    PREFER_KEYWORDS,
    REVIEW_KEYWORDS,
)


class TestLiveCatalogFeed(unittest.TestCase):

    def test_is_free(self):
        self.assertTrue(_is_free("ox-alpha", None, "free_trial"))
        self.assertTrue(_is_free("qwen/qwen-2.5-coder:free", {}))
        self.assertTrue(_is_free("stealth/ox-alpha", None))
        self.assertFalse(_is_free("paid/model", {"prompt": "0.01", "completion": "0.02"}))
        self.assertTrue(_is_free("free/model", {"prompt": "0", "completion": "0"}))

    @patch("scripts.live_catalog_feed._token")
    @patch("urllib.request.urlopen")
    def test_poll_provider_success(self, mock_urlopen, mock_token):
        mock_token.return_value = "fake-token"
        response_data = {
            "data": [
                {"id": "model-1:free", "pricing": {"prompt": "0", "completion": "0"}, "context_length": 8192},
                {"id": "ox-alpha", "context_length": 1000000},
            ]
        }
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(response_data).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        rows, state = poll_provider("openrouter")
        self.assertEqual(state, "live")
        self.assertTrue(any(r["id"] == "model-1:free" for r in rows))

    @patch("scripts.live_catalog_feed.poll_provider")
    def test_load_eligible_single_pass(self, mock_poll):
        import shutil, tempfile
        mock_poll.side_effect = lambda provider: (
            [
                {"provider": provider, "id": f"{provider}/free-1", "free": True},
                {"provider": provider, "id": f"{provider}/paid-1", "free": False},
            ],
            "live",
        )
        temp_dir = tempfile.mkdtemp()
        try:
            feed = load_eligible(providers=["openrouter", "felo"], cache_dir=temp_dir)
            self.assertEqual(feed["catalog_state"], "live")
            self.assertEqual(len(feed["eligible"]), 2)
            self.assertIn("openrouter", feed["eligible_ids_by_provider"])
            self.assertIn("felo", feed["eligible_ids_by_provider"])
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_peer_candidates_for_role(self):
        feed = {
            "eligible": [
                {"provider": "openrouter", "id": "qwen/qwen-2.5-coder:free"},
                {"provider": "felo", "id": "ox-alpha"},
                {"provider": "omni", "id": "deepseek/deepseek-r1:free"},
            ]
        }
        peers = peer_candidates_for_role("review", feed)
        self.assertTrue(len(peers) > 0)
        providers = [p[0] for p in peers]
        self.assertIn("openrouter", providers)


if __name__ == "__main__":
    unittest.main()
