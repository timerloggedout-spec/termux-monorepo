from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "ci"))

from validate_siglary_mandate import (  # noqa: E402
    CROSSWALK_TOKENS,
    EXPECTED_RULE_IDS,
    MATRICE,
    MANDATE,
    avoid_matches,
    crosswalk_tokens,
    rule_ids,
)


class SiglaryMandateTests(unittest.TestCase):
    def test_rule_id_registry_parser_preserves_all_ids_in_order(self):
        rows = "\n".join(f"| {rule_id} | DO | example |" for rule_id in EXPECTED_RULE_IDS)
        text = f"## SG rule registry and enforcement boundary\n{rows}\n### Automated coverage\n"
        self.assertEqual(rule_ids(text), EXPECTED_RULE_IDS)

    def test_repository_registry_matches_expected_ids(self):
        self.assertEqual(rule_ids((ROOT / MANDATE).read_text(encoding="utf-8")), EXPECTED_RULE_IDS)

    def test_repository_crosswalk_contains_every_supplied_symbol(self):
        observed = crosswalk_tokens((ROOT / MATRICE).read_text(encoding="utf-8"))
        self.assertTrue(set(CROSSWALK_TOKENS).issubset(observed))

    def test_avoid_vocabulary_is_case_insensitive(self):
        self.assertEqual(avoid_matches("No, not, NEVER, and don't."), ["No", "not", "NEVER", "don't"])

    def test_inline_code_remains_literal(self):
        self.assertEqual(avoid_matches("Use `not` as an exact token."), [])

    def test_link_destination_is_excluded(self):
        self.assertEqual(avoid_matches("Read [the guide](https://example.test/not-here)."), [])

    def test_exact_quotes_are_excluded(self):
        self.assertEqual(avoid_matches('Preserve "Never reword this source quote."'), [])
        self.assertEqual(avoid_matches("Preserve ‘not in this quoted passage’ verbatim."), [])
        self.assertEqual(avoid_matches("Preserve 'not in this source passage' verbatim."), [])

    def test_fenced_and_blockquote_source_text_is_excluded(self):
        self.assertEqual(avoid_matches("> Never alter this quotation.\n\n```text\nNot source prose.\n```"), [])

    def test_raw_url_is_excluded(self):
        self.assertEqual(avoid_matches("See https://example.test/not-found for details."), [])

    def test_nonlisted_words_do_not_match(self):
        self.assertEqual(avoid_matches("Notebook notes and noteworthy items."), [])


if __name__ == "__main__":
    unittest.main()
