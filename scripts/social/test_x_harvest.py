#!/usr/bin/env python3
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from x_harvest import (XHttpError, build_payload, classify_plane, compute_delta,
                       main, merge_records, normalize, refresh_access_token,
                       snapshot_hash)
import x_oauth

USERS = {"42": {"id": "42", "username": "someone", "name": "Some One"}}
TWEET = {"id": "100", "author_id": "42", "text": "a post about termux workflows",
         "created_at": "2026-10-01T00:00:00Z",
         "public_metrics": {"like_count": 5, "retweet_count": 1}}


class XHarvestTests(unittest.TestCase):
    def test_bookmark_is_metadata_only(self):
        rec = normalize(TWEET, USERS, "bookmark", "owner", {}, "2026-10-29T00:00:00Z")
        self.assertIsNone(rec["text_excerpt"])
        self.assertEqual(len(rec["text_sha256"]), 64)
        self.assertEqual(rec["url"], "https://x.com/someone/status/100")

    def test_like_keeps_excerpt_and_marketing_plane(self):
        rec = normalize(TWEET, USERS, "like", "owner", {}, "2026-10-29T00:00:00Z")
        self.assertIn("termux", rec["text_excerpt"])
        self.assertEqual(rec["plane"], "marketing")
        self.assertEqual(rec["plane_basis"], "term:termux")

    def test_personal_default_and_override(self):
        plane, basis = classify_plane("gardening notes", "someone", "owner", {}, "7")
        self.assertEqual((plane, basis), ("personal", "default_no_marketing_signal"))
        plane, basis = classify_plane("gardening", "someone", "owner", {"7": "marketing"}, "7")
        self.assertEqual((plane, basis), ("marketing", "owner_override"))

    def test_own_author_is_marketing(self):
        plane, basis = classify_plane("hello", "Owner", "owner", {}, "9")
        self.assertEqual(plane, "marketing")

    def test_merge_unions_signals_and_keeps_first_capture(self):
        like = normalize(TWEET, USERS, "like", "owner", {}, "2026-10-29T00:00:00Z")
        bm = normalize(TWEET, USERS, "bookmark", "owner", {}, "2026-10-30T00:00:00Z")
        merged = merge_records([bm], [like])
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["signals"], ["bookmark", "like"])
        self.assertEqual(merged[0]["first_captured_at"], "2026-10-29T00:00:00Z")

    def test_delta_and_payload_counts(self):
        prev = [normalize(TWEET, USERS, "like", "owner", {}, "t0")]
        cur = merge_records([normalize(TWEET, USERS, "bookmark", "owner", {}, "t1")], prev)
        delta = compute_delta(prev, cur)
        self.assertTrue(delta["available"])
        self.assertEqual(delta["signal_changed"][0]["to"], ["bookmark", "like"])
        payload = build_payload({"id": "1", "username": "owner"}, cur, "t1", delta=delta)
        self.assertEqual(payload["counts"]["both"], 1)
        self.assertEqual(len(payload["snapshot_hash"]), 64)
        self.assertEqual(snapshot_hash(cur), snapshot_hash(json.loads(json.dumps(cur))))

    def test_defer_without_token_writes_nothing(self):
        env = dict(os.environ)
        env.pop("X_OAUTH2_USER_TOKEN", None)
        old = os.environ.copy()
        os.environ.clear(); os.environ.update(env)
        try:
            with tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp) / "idx.json"; md = Path(tmp) / "mx.md"
                rc = main(["--output", str(out), "--markdown", str(md), "--defer-ok"])
                self.assertEqual(rc, 0)
                self.assertFalse(out.exists())
        finally:
            os.environ.clear(); os.environ.update(old)

    def test_harvest_via_stub_fetch(self):
        def fetch(path, token, params=None):
            if path == "/users/me":
                return {"data": {"id": "1", "username": "owner", "name": "Owner"}}
            return {"data": [TWEET], "includes": {"users": [USERS["42"]]}, "meta": {}}
        env_old = os.environ.get("X_OAUTH2_USER_TOKEN")
        os.environ["X_OAUTH2_USER_TOKEN"] = "test-token-not-real"
        try:
            with tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp) / "idx.json"; md = Path(tmp) / "mx.md"
                rc = main(["--output", str(out), "--markdown", str(md)], fetch=fetch)
                self.assertEqual(rc, 0)
                payload = json.loads(out.read_text())
                self.assertEqual(payload["counts"]["total"], 1)
                self.assertEqual(payload["counts"]["both"], 1)  # stub returns it for both endpoints
                self.assertIn("## Marketing plane", md.read_text())
        finally:
            if env_old is None:
                os.environ.pop("X_OAUTH2_USER_TOKEN", None)
            else:
                os.environ["X_OAUTH2_USER_TOKEN"] = env_old


    def test_refresh_access_token_shape(self):
        seen = {}

        def poster(url, form, client_id, client_secret):
            seen.update(form)
            return {"access_token": "acc", "refresh_token": "rotated"}

        access, rotated = refresh_access_token("cid", None, "rt0", poster=poster)
        self.assertEqual((access, rotated), ("acc", "rotated"))
        self.assertEqual(seen["grant_type"], "refresh_token")
        self.assertEqual(seen["refresh_token"], "rt0")

    def test_authorize_url_is_pkce_s256(self):
        import urllib.parse as up
        url = x_oauth.authorize_url("cid", "http://localhost:8765/callback")
        q = up.parse_qs(up.urlparse(url).query)
        self.assertEqual(q["code_challenge_method"], ["S256"])
        self.assertIn("offline.access", q["scope"][0])
        self.assertIn("bookmark.read", q["scope"][0])


if __name__ == "__main__":
    unittest.main()
