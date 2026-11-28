import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.localization import validate as localization
from scripts.ops import render_teammate_portal_status as renderer


class LocalizationReviewRegressionTests(unittest.TestCase):
    def test_mapping_schema_rejects_missing_locale_state_and_fallback(self):
        original_read = localization.read

        def altered_read(path):
            data = original_read(path)
            if path == "localization/mappings/teammate-portal.json":
                for key in ("locale", "state", "fallback"):
                    data["entries"][0].pop(key, None)
            return data

        with patch.object(localization, "read", side_effect=altered_read):
            errors = localization.validate()
        self.assertTrue(any("schema" in error.lower() for error in errors), errors)

    def test_freshness_hash_mismatch_fails_even_when_manifest_says_fresh(self):
        original_read = localization.read

        def altered_read(path):
            data = original_read(path)
            if path == "localization/manifests/teammate-portal.json":
                data["translations"][0]["freshness"]["source_hash"] = "git-blob:stale"
                data["translations"][0]["freshness"]["state"] = "fresh"
            return data

        with patch.object(localization, "read", side_effect=altered_read):
            errors = localization.validate()
        self.assertTrue(any("source hash" in error.lower() for error in errors), errors)

    def test_locale_registry_rejects_malformed_language_tag(self):
        original_read = localization.read

        def altered_read(path):
            data = original_read(path)
            if path == "localization/registry/locales.json":
                next(item for item in data["locales"] if item["id"] == "ur")["language_tag"] = "ur-"
            return data

        with patch.object(localization, "read", side_effect=altered_read):
            errors = localization.validate()
        self.assertTrue(any("language_tag" in error for error in errors), errors)

    def test_locale_tag_must_match_registry_id(self):
        original_read = localization.read

        def altered_read(path):
            data = original_read(path)
            if path == "localization/registry/locales.json":
                next(item for item in data["locales"] if item["id"] == "ur")["language_tag"] = "en"
            return data

        with patch.object(localization, "read", side_effect=altered_read):
            errors = localization.validate()
        self.assertTrue(any("must match its locale id" in error for error in errors), errors)

    def test_manifest_catalog_must_match_translation_locale(self):
        original_read = localization.read

        def altered_read(path):
            data = original_read(path)
            if path == "localization/manifests/teammate-portal.json":
                data["translations"][0]["catalog"] = "localization/glossaries/teammate-portal/ur.json"
            return data

        with patch.object(localization, "read", side_effect=altered_read):
            errors = localization.validate()
        self.assertTrue(any("catalog must be localization/catalogs/teammate-portal/ur.json" in error for error in errors), errors)
    def test_feedback_schema_requires_nonempty_translation_identifiers(self):
        schema = json.loads(Path("localization/schemas/feedback.schema.json").read_text(encoding="utf-8"))
        properties = schema["properties"]
        self.assertEqual(properties["message_key"].get("minLength"), 1)
        self.assertEqual(properties["translation_revision"].get("minLength"), 1)

    def test_doe_cohort_pins_exactly_twelve_message_keys(self):
        design = json.loads(Path("localization/doe/urdu-portal-v1/DESIGN.json").read_text(encoding="utf-8"))
        keys = design["cohort"].get("task_keys", [])
        source = json.loads(Path("localization/catalogs/teammate-portal/en.json").read_text(encoding="utf-8"))
        self.assertEqual(len(keys), 12)
        self.assertEqual(len(set(keys)), 12)
        self.assertTrue(set(keys).issubset(source["messages"]))

    def test_catalog_root_can_be_overridden_for_fallback_renderer(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            catalog_dir = root / "localization" / "catalogs" / "teammate-portal"
            catalog_dir.mkdir(parents=True)
            (catalog_dir / "en.json").write_text(json.dumps({"messages": {"page.title": "Tooling catalog"}}), encoding="utf-8")
            with patch.dict(os.environ, {"POLYGLOT_REPO_ROOT": temp}):
                messages = renderer.load_catalog("en")
        self.assertEqual(messages["page.title"], "Tooling catalog")

    def test_stale_urdu_catalog_falls_back_to_source_messages(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            catalog_dir = root / "localization" / "catalogs" / "teammate-portal"
            catalog_dir.mkdir(parents=True)
            (catalog_dir / "en.json").write_text(json.dumps({"messages": {"page.title": "English fallback"}}), encoding="utf-8")
            (catalog_dir / "ur.json").write_text(json.dumps({"messages": {"page.title": "پرانا ترجمہ"}}), encoding="utf-8")
            manifest_dir = root / "localization" / "manifests"
            manifest_dir.mkdir(parents=True)
            (manifest_dir / "teammate-portal.json").write_text(json.dumps({
                "translations": [{
                    "locale": "ur",
                    "source_catalog": "localization/catalogs/teammate-portal/en.json",
                    "freshness": {"source_hash": "git-blob:stale", "state": "fresh"},
                    "review": {"status": "review_required"},
                    "publication": "preview_only"
                }]
            }), encoding="utf-8")
            with patch.dict(os.environ, {"POLYGLOT_REPO_ROOT": temp}):
                messages = renderer.load_catalog("ur")
        self.assertEqual(messages["page.title"], "English fallback")

    def test_stale_urdu_page_uses_source_language_metadata(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            catalog_dir = root / "localization" / "catalogs" / "teammate-portal"
            catalog_dir.mkdir(parents=True)
            source = {"messages": {
                "page.title": "English fallback",
                "nav.language": "Language",
                "nav.english": "English",
                "nav.urdu": "Urdu",
                "content.english_fallback": "English source content",
                "status.review_required": "Awaiting native review",
            }}
            (catalog_dir / "en.json").write_text(json.dumps(source), encoding="utf-8")
            (catalog_dir / "ur.json").write_text(json.dumps({"messages": {"page.title": "پرانا"}}), encoding="utf-8")
            manifest_dir = root / "localization" / "manifests"
            manifest_dir.mkdir(parents=True)
            (manifest_dir / "teammate-portal.json").write_text(json.dumps({
                "translations": [{
                    "locale": "ur",
                    "source_catalog": "localization/catalogs/teammate-portal/en.json",
                    "freshness": {"source_hash": "git-blob:stale", "state": "fresh"},
                    "review": {"status": "review_required"},
                    "publication": "preview_only",
                }]
            }), encoding="utf-8")
            with patch.dict(os.environ, {"POLYGLOT_REPO_ROOT": temp}):
                rendered = renderer.page("اردو", "<p>English fallback</p>", "ur", title_key="page.title")
        self.assertIn('<html lang="en" dir="ltr">', rendered)
        self.assertIn("<title>English fallback</title>", rendered)
        self.assertNotIn("body{direction:rtl", rendered)

    def test_page_title_comes_from_selected_catalog(self):
        messages = {
            "page.title": "Catalog page title",
            "nav.language": "Language",
            "nav.english": "English",
            "nav.urdu": "Urdu",
        }
        with patch.object(renderer, "load_catalog", return_value=messages):
            page = renderer.page("Hard-coded title", "<p>body</p>", "en", title_key="page.title")
        self.assertIn("<title>Catalog page title</title>", page)

    def test_urdu_review_notice_reflects_manifest_state(self):
        messages = {
            "status.review_required": "Awaiting native review",
            "nav.language": "زبان",
            "nav.english": "انگریزی",
            "nav.urdu": "اردو",
            "page.title": "اردو",
        }
        manifest = {
            "translations": [{
                "locale": "ur",
                "review": {"status": "review_required"},
                "publication": "preview_only",
            }]
        }
        with patch.object(renderer, "load_catalog", return_value=messages), patch.object(renderer, "load_manifest", return_value=manifest):
            notice = renderer.review_notice("ur")
        self.assertIn("review_required", notice)
        self.assertIn("preview_only", notice)

    def test_urdu_reference_links_target_root_level_documents(self):
        messages = {
            "page.title": "عنوان",
            "page.description": "تفصیل",
            "page.separation": "علیحدگی",
            "status.done": "مکمل",
            "status.source": "ماخذ",
            "section.done_board": "بورڈ",
            "section.dispatch": "ڈسپیچ",
            "section.dispatch_label": "ٹیم میٹ پورٹل",
            "section.reference": "حوالہ",
            "section.route": "راستہ",
            "content.empty_dispatch": "کوئی آئٹم نہیں",
        }
        rendered = renderer.render_body(
            messages, [], 0, "open", "source", "abcdef0", "now", [],
            renderer.DOCS, "owner/repo", 1, locale="ur",
        )
        self.assertIn('href="../plan.html"', rendered)
        self.assertNotIn('href="plan.html"', rendered)

    def test_shell_labels_follow_the_selected_catalog(self):
        messages = {
            "page.title": "Catalog title",
            "page.description": "Catalog description",
            "page.separation": "Catalog separation",
            "status.done": "Catalog done",
            "status.source": "Catalog source",
            "section.done_board": "Catalog board",
            "section.dispatch": "Catalog dispatch",
            "section.dispatch_label": "Catalog label",
            "section.reference": "Catalog references",
            "section.route": "Catalog workflow",
            "content.empty_dispatch": "Catalog empty",
        }
        rendered = renderer.render_body(
            messages, [], 0, "open", "source", "abcdef0", "now", [],
            renderer.DOCS, "owner/repo", 1,
        )
        self.assertIn("<h2>Catalog workflow</h2>", rendered)
    def test_publish_workflow_fetches_renderer_and_both_catalogs_as_one_tooling_unit(self):
        workflow = Path(".github/workflows/teammate-portal-status-publish.yml").read_text(encoding="utf-8")
        self.assertIn("tooling_ref", workflow)
        self.assertIn("localization/catalogs/teammate-portal/en.json", workflow)
        self.assertIn("localization/catalogs/teammate-portal/ur.json", workflow)
        self.assertIn('for asset in "$renderer" "$en_catalog" "$ur_catalog" "$translation_manifest"; do', workflow)
        self.assertNotIn('if [ ! -f "$renderer"', workflow)


if __name__ == "__main__":
    unittest.main()
