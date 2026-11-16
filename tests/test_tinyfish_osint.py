"""Tests for tinyfish_osint — network-free (transport injected/mocked)."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "services"))
import tinyfish_osint as tf


class ValidateUrl(unittest.TestCase):
    def test_public_ok(self):
        self.assertEqual(tf.validate_public_url("https://kiroween.devpost.com/project-gallery"),
                         "https://kiroween.devpost.com/project-gallery")

    def test_scheme_refused(self):
        with self.assertRaises(ValueError):
            tf.validate_public_url("ftp://example.com/x")

    def test_loopback_refused(self):
        with self.assertRaises(ValueError):
            tf.validate_public_url("http://127.0.0.1/admin")
        with self.assertRaises(ValueError):
            tf.validate_public_url("http://localhost/x")

    def test_private_ip_refused(self):
        with self.assertRaises(ValueError):
            tf.validate_public_url("http://192.168.1.10/x")


class Chunking(unittest.TestCase):
    def test_chunks(self):
        self.assertEqual(list(tf.chunked(list(range(120)), 50)),
                         [list(range(50)), list(range(50, 100)), list(range(100, 120))])


class Defer(unittest.TestCase):
    def test_defer_no_key_writes_nothing(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "env.json"
            with mock.patch.dict(os.environ, {}, clear=True):
                rc = tf.main(["--mode", "fetch", "--url", "https://example.com",
                              "--output", str(out), "--defer-ok"])
            self.assertEqual(rc, 0)
            self.assertFalse(out.exists())

    def test_no_key_no_defer_flag_errors(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "env.json"
            with mock.patch.dict(os.environ, {}, clear=True):
                rc = tf.main(["--mode", "search", "--query", "x",
                              "--output", str(out)])
            self.assertEqual(rc, 2)


class EnvelopeFlow(unittest.TestCase):
    def test_fetch_ok_envelope(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "env.json"
            fake = [{"results": [{"url": "https://example.com", "markdown": "hi"}]}]
            with mock.patch.dict(os.environ, {"TINYFISH_API_KEY": "test-key"}):
                with mock.patch.object(tf, "run_fetch", return_value=fake):
                    rc = tf.main(["--mode", "fetch", "--url", "https://example.com",
                                  "--output", str(out)])
            self.assertEqual(rc, 0)
            env = json.loads(out.read_text())
            self.assertEqual(env["schema"], "tinyfish-osint/v1")
            self.assertEqual(env["mode"], "fetch")
            self.assertEqual(env["status"], "ok")
            self.assertEqual(env["results"], fake)
            self.assertEqual(env["quota_slice"], "github:scraping-tools")

    def test_search_ok_envelope(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "env.json"
            fake = {"results": [{"url": "https://example.com", "title": "t"}]}
            with mock.patch.dict(os.environ, {"TINYFISH_API_KEY": "test-key"}):
                with mock.patch.object(tf, "run_search", return_value=fake):
                    rc = tf.main(["--mode", "search", "--query", "kiroween gallery",
                                  "--output", str(out)])
            self.assertEqual(rc, 0)
            env = json.loads(out.read_text())
            self.assertEqual(env["mode"], "search")
            self.assertEqual(env["status"], "ok")

    def test_fetch_cap_enforced(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "env.json"
            urls = ["--url", "https://example.com"] * (tf.FETCH_DAILY_CAP + 1)
            argv = ["--mode", "fetch", "--output", str(out)] + urls
            with mock.patch.dict(os.environ, {"TINYFISH_API_KEY": "test-key"}):
                rc = tf.main(argv)
            self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
