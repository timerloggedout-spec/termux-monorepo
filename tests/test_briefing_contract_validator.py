import unittest

from scripts.ci.briefing_contract_validator import validate_briefing, validate_registry


def valid_briefing():
    return {
        "schema_version": "1.0",
        "briefing_date": "2026-10-17",
        "generated_at": "2026-10-17T09:30:00Z",
        "contract": {
            "spec": "docs/briefing/DAILY-DIGEST-SPEC.md",
            "ingest": "docs/research/BRIEFING-INGEST.md",
            "procurement": "docs/research/FOSS-PROCUREMENT-MATRIX.md",
            "radar": "docs/research/FORESIGHT-RADAR.md",
            "source_registry": "config/foresight_digest_sources.json",
        },
        "items": [{
            "headline": "A credible release",
            "horizon": "H1",
            "evidence_status": "confirmed",
            "summary": "A concise, evidence-backed summary.",
            "why_it_matters": "It changes a practical engineering choice.",
            "opportunity_or_procurement": "Prototype behind a reversible adapter.",
            "monorepo_relevance": "Direct relevance to an existing integration lane.",
            "sources": [{"url": "https://example.org/release", "source_type": "official_release"}],
            "confidence": "high",
            "unresolved_questions": ["Does the behavior hold on Android?"],
            "image_query": "abstract software architecture",
        }],
    }


class BriefingContractValidatorTests(unittest.TestCase):
    def test_accepts_valid_briefing(self):
        self.assertEqual(validate_briefing(valid_briefing()), [])

    def test_rejects_missing_provenance_and_invalid_horizon(self):
        briefing = valid_briefing()
        briefing["items"][0]["sources"] = []
        briefing["items"][0]["horizon"] = "certain"
        errors = validate_briefing(briefing)
        self.assertTrue(any("items[0].sources" in error for error in errors))
        self.assertTrue(any("items[0].horizon" in error for error in errors))

    def test_rejects_non_utc_timestamp_and_wrong_contract(self):
        briefing = valid_briefing()
        briefing["generated_at"] = "2026-10-17T09:30:00-07:00"
        briefing["contract"]["radar"] = "some/other/file.md"
        errors = validate_briefing(briefing)
        self.assertTrue(any("generated_at" in error for error in errors))
        self.assertTrue(any("contract.radar" in error for error in errors))

    def test_rejects_empty_or_overfilled_digest(self):
        briefing = valid_briefing()
        briefing["items"] = []
        self.assertTrue(any("1 to 5" in error for error in validate_briefing(briefing)))
        briefing["items"] = [valid_briefing()["items"][0] for _ in range(6)]
        self.assertTrue(any("1 to 5" in error for error in validate_briefing(briefing)))

    def test_accepts_valid_registry_and_rejects_duplicate_ids(self):
        registry = {
            "schema_version": 2,
            "resource_families": [
                {"id": "otel", "name": "OpenTelemetry", "role": "telemetry",
                 "url": "https://opentelemetry.io/"},
                {"id": "otel", "name": "Duplicate", "role": "test",
                 "url": "https://example.org/"},
            ],
        }
        errors = validate_registry(registry)
        self.assertEqual(sum("duplicate resource id" in error for error in errors), 1)

    def test_rejects_non_http_sources(self):
        briefing = valid_briefing()
        briefing["items"][0]["sources"][0]["url"] = "file:///etc/passwd"
        self.assertTrue(any("absolute HTTP(S) URL" in error
                            for error in validate_briefing(briefing)))


if __name__ == "__main__":
    unittest.main()
