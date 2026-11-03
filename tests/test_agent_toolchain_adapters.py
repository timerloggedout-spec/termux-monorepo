import unittest

from scripts.integrations.agent_toolchain import (
    normalize_context7_document,
    normalize_context_dev_result,
    normalize_hapi_server,
    validate_observation,
)


CAPTURED = "2026-11-03T06:00:00Z"


class HapiRegistryNormalizerTests(unittest.TestCase):
    def setUp(self):
        self.record = {
            "server": {
                "name": "example.org/weather",
                "title": "Weather MCP",
                "version": "1.2.0",
                "description": "Read-only weather metadata.",
                "remotes": [
                    {"type": "streamable-http", "url": "https://mcp.example.org/weather?token=do-not-retain#tools"},
                    {"type": "sse", "url": "https://mcp.example.org/events"},
                ],
                "capabilities": ["tools", "resources"],
                "futureField": {"private": "must not be copied"},
            },
            "_meta": {
                "io.modelcontextprotocol.registry/official": {
                    "status": "active",
                    "publishedAt": "2026-10-01T00:00:00Z",
                    "updatedAt": "2026-10-02T00:00:00Z",
                    "isLatest": True,
                }
            },
        }

    def test_normalizes_stable_identity_and_remote_transport(self):
        result = normalize_hapi_server(self.record, CAPTURED, "req-hapi-1")
        self.assertEqual(result["record_key"], "example.org/weather@1.2.0")
        self.assertEqual(result["identity"]["version"], "1.2.0")
        self.assertEqual(
            [remote["transport"] for remote in result["data"]["remotes"]],
            ["streamable-http", "sse"],
        )
        self.assertEqual(
            result["data"]["remotes"][0]["endpoint"],
            "https://mcp.example.org/weather",
        )
        self.assertEqual(result["source"]["provider_request_id"], "req-hapi-1")

    def test_discovery_never_implies_security_or_execution_admission(self):
        result = normalize_hapi_server(self.record, CAPTURED)
        self.assertEqual(result["trust"]["security_review_status"], "not_reviewed")
        self.assertEqual(result["trust"]["admission_status"], "not_admitted")
        self.assertFalse(result["trust"]["execution_allowed"])

    def test_unknown_fields_are_named_but_values_are_not_copied(self):
        result = normalize_hapi_server(self.record, CAPTURED)
        self.assertIn("futureField", result["data"]["unmapped_field_names"])
        self.assertNotIn("private", str(result))

    def test_versions_have_distinct_stable_keys(self):
        first = normalize_hapi_server(self.record, CAPTURED)
        second_record = {
            "server": dict(self.record["server"], version="2.0.0"),
            "_meta": self.record["_meta"],
        }
        second = normalize_hapi_server(second_record, CAPTURED)
        self.assertNotEqual(first["record_key"], second["record_key"])

    def test_rejects_missing_identity_or_version(self):
        for field in ("name", "version"):
            record = {"server": dict(self.record["server"])}
            record["server"].pop(field)
            with self.subTest(field=field), self.assertRaises(ValueError):
                normalize_hapi_server(record, CAPTURED)

    def test_rejects_remote_urls_with_credentials(self):
        record = {"server": dict(self.record["server"])}
        record["server"]["remotes"] = [
            {"type": "streamable-http", "url": "https://user:pass@mcp.example.org"}
        ]
        with self.assertRaises(ValueError):
            normalize_hapi_server(record, CAPTURED)

    def test_rejects_non_https_remote_endpoint(self):
        record = {"server": dict(self.record["server"])}
        record["server"]["remotes"] = [
            {"type": "streamable-http", "url": "http://mcp.example.org"}
        ]
        with self.assertRaises(ValueError):
            normalize_hapi_server(record, CAPTURED)


class ContextEvidenceNormalizerTests(unittest.TestCase):
    def test_context7_requires_explicit_version(self):
        with self.assertRaises(ValueError):
            normalize_context7_document(
                {"title": "Docs", "content": "example"},
                "/org/library",
                None,
                CAPTURED,
            )

    def test_context7_accepts_version_in_library_id(self):
        result = normalize_context7_document(
            {"title": "Docs", "content": "Versioned example"},
            "/org/library/v4.2.0",
            None,
            CAPTURED,
        )
        self.assertEqual(result["identity"]["library_id"], "/org/library/v4.2.0")
        self.assertEqual(result["identity"]["version"], "v4.2.0")

    def test_context7_accepts_explicit_version_with_unversioned_id(self):
        result = normalize_context7_document(
            {"title": "Docs", "content": "Versioned example"},
            "/org/library",
            "4.2.0",
            CAPTURED,
        )
        self.assertEqual(result["record_key"], "/org/library@4.2.0")

    def test_context7_rejects_conflicting_versions(self):
        with self.assertRaises(ValueError):
            normalize_context7_document(
                {"title": "Docs"},
                "/org/library/v4.2.0",
                "5.0.0",
                CAPTURED,
            )

    def test_context7_preserves_source_refs_and_bounds_excerpt(self):
        result = normalize_context7_document(
            {
                "title": "Docs",
                "content": "x" * 25000,
                "sources": [{"url": "https://docs.example.org/v4/guide#section", "title": "Guide"}],
            },
            "/org/library",
            "4.2.0",
            CAPTURED,
            "req-context7-1",
        )
        self.assertEqual(result["data"]["source_refs"][0]["url"], "https://docs.example.org/v4/guide")
        self.assertEqual(len(result["data"]["excerpt"]), 20000)
        self.assertTrue(result["data"]["truncated"])
        self.assertEqual(result["source"]["provider_request_id"], "req-context7-1")
        self.assertNotIn("query", result)

    def test_context_dev_strips_query_and_fragment(self):
        result = normalize_context_dev_result(
            {
                "url": "https://research.example.org/path?token=secret&query=private#section",
                "title": "Research",
                "snippet": "An attributed excerpt.",
            },
            CAPTURED,
            "req-context-1",
        )
        self.assertEqual(result["data"]["canonical_url"], "https://research.example.org/path")
        self.assertTrue(result["data"]["url_query_redacted"])
        self.assertTrue(result["trust"]["content_untrusted"])
        self.assertNotIn("secret", str(result))
        self.assertNotIn("private", str(result))

    def test_context_dev_rejects_credentials_and_non_http_urls(self):
        for url in ("https://user:pass@example.org/path", "file:///etc/passwd", "javascript:alert(1)"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                normalize_context_dev_result({"url": url}, CAPTURED)

    def test_context_dev_bounds_excerpt_and_marks_truncation(self):
        result = normalize_context_dev_result(
            {"url": "https://example.org", "content": "z" * 6000},
            CAPTURED,
        )
        self.assertEqual(len(result["data"]["excerpt"]), 4000)
        self.assertTrue(result["data"]["truncated"])

    def test_shared_contract_validator_rejects_mutated_trust_state(self):
        result = normalize_hapi_server(
            {"server": {"name": "example.org/server", "version": "1.0.0"}},
            CAPTURED,
        )
        result["trust"]["execution_allowed"] = True
        self.assertTrue(validate_observation(result))


if __name__ == "__main__":
    unittest.main()
