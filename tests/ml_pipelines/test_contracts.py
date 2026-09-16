import unittest

from ml_pipelines.contracts import PipelineError, assert_safe, digest, redacted


class ContractTests(unittest.TestCase):
    def test_redacts_token_field(self):
        out = redacted({"token": "secret", "number": 1})
        self.assertNotIn("token", out)
        self.assertEqual(out["number"], 1)

    def test_redacts_credential_shaped_string(self):
        out = redacted({"title": "use ghp_abcdefghijk123 for demo"})
        self.assertIn("[REDACTED]", out["title"])

    def test_digest_stable(self):
        a = digest({"b": 1, "a": 2})
        b = digest({"a": 2, "b": 1})
        self.assertEqual(a, b)

    def test_assert_safe_rejects_forbidden(self):
        with self.assertRaises(PipelineError):
            assert_safe({"password": "nope"})


if __name__ == "__main__":
    unittest.main()
