import importlib.util
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location("sanitizer", Path(__file__).parents[1] / "tools" / "sanitize_codex_blobs.py")
sanitizer = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(sanitizer)


class RedactionTests(unittest.TestCase):
    def test_redacts_value_but_keeps_code(self):
        clean, counts = sanitizer.redact('client = Api(token="ghp_abcdefghijklmnopqrstuvwxyz123456")\nprint(client)\n')
        self.assertIn('token="[REDACTED]"', clean)
        self.assertIn("print(client)", clean)
        self.assertEqual(sum(counts.values()), 1)

    def test_redacts_standalone_github_token(self):
        clean, counts = sanitizer.redact("ghp_abcdefghijklmnopqrstuvwxyz123456")
        self.assertEqual(clean, "[REDACTED]")
        self.assertEqual(counts["github"], 1)

    def test_keeps_environment_reference(self):
        source = 'token = os.environ["API_TOKEN"]\n'
        self.assertEqual(sanitizer.redact(source)[0], source)

    def test_redacts_private_key(self):
        clean, counts = sanitizer.redact("-----BEGIN PRIVATE KEY-----\nabc\n-----END PRIVATE KEY-----")
        self.assertEqual(clean, "[REDACTED PRIVATE KEY]")
        self.assertEqual(counts["private_key"], 1)

    def test_redacts_common_machine_credentials(self):
        source = "AKIA1234567890ABCDEF eyJabcdefghijk.abcdefghijk.abcdefghijk"
        clean, counts = sanitizer.redact(source)
        self.assertEqual(clean, "[REDACTED] [REDACTED]")
        self.assertEqual(counts["aws_access_key"], 1)
        self.assertEqual(counts["jwt"], 1)
