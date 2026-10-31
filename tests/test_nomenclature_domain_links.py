import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
LINKS_PATH = ROOT / "docs/proposals/active/notation-sets/nomenclature-matrix/DOMAIN-COMPOSITION-LINKS.json"
NOMENCLATURE_PATH = ROOT / "docs/proposals/active/notation-sets/nomenclature-matrix/seed.json"
DOMAIN_PATH = ROOT / "docs/proposals/active/domain-composition-matrix/seed.json"
VALIDATOR_PATH = ROOT / "scripts/ci/validate_nomenclature_domain_links.py"
SPEC = importlib.util.spec_from_file_location("nomenclature_domain_links", VALIDATOR_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

class NomenclatureDomainLinkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.links = json.loads(LINKS_PATH.read_text(encoding="utf-8"))
        cls.nomenclature = json.loads(NOMENCLATURE_PATH.read_text(encoding="utf-8"))
        cls.domain = json.loads(DOMAIN_PATH.read_text(encoding="utf-8"))

    def test_checked_in_links_validate(self):
        self.assertEqual([], MODULE.validate(self.links, self.nomenclature, self.domain))

    def test_links_remain_candidate_only(self):
        self.assertTrue(all(item["status"] == "candidate" for item in self.links["links"]))
        self.assertIn("candidate only", self.links["authority_boundary"])

    def test_unknown_concept_is_rejected(self):
        bad = copy.deepcopy(self.links)
        bad["links"][0]["concept_id"] = "missing.concept"
        self.assertTrue(any("unknown nomenclature concept" in e for e in MODULE.validate(bad, self.nomenclature, self.domain)))

    def test_unknown_target_is_rejected(self):
        bad = copy.deepcopy(self.links)
        bad["links"][0]["target_id"] = "missing-domain"
        self.assertTrue(any("references unknown domain" in e for e in MODULE.validate(bad, self.nomenclature, self.domain)))

    def test_relation_must_match_target_type(self):
        bad = copy.deepcopy(self.links)
        bad["links"][0]["relation"] = "describes_operation"
        self.assertTrue(any("invalid for target_type" in e for e in MODULE.validate(bad, self.nomenclature, self.domain)))

    def test_cross_domain_link_is_rejected(self):
        bad = copy.deepcopy(self.links)
        bad["links"][0]["target_id"] = "haskell"
        self.assertTrue(any("domain scope disagrees" in e for e in MODULE.validate(bad, self.nomenclature, self.domain)))

    def test_accepted_link_requires_real_review_metadata(self):
        bad = copy.deepcopy(self.links)
        bad["links"][0].update(status="accepted", reviewer=" ", reviewed_on=None)
        errors = MODULE.validate(bad, self.nomenclature, self.domain)
        self.assertTrue(any("nonblank reviewer" in e for e in errors))
        self.assertTrue(any("reviewed_on" in e for e in errors))

    def test_source_path_mismatch_is_rejected(self):
        bad = copy.deepcopy(self.links)
        bad["source_contracts"]["nomenclature"]["path"] = "some/other/seed.json"
        self.assertTrue(any("nomenclature source path mismatch" in e for e in MODULE.validate(bad, self.nomenclature, self.domain)))

    def test_accepted_link_requires_canonical_review_date(self):
        for reviewed_on in ("20261030", "2026-1-30", "2026-02-30"):
            with self.subTest(reviewed_on=reviewed_on):
                bad = copy.deepcopy(self.links)
                bad["links"][0].update(status="accepted", reviewer="independent reviewer", reviewed_on=reviewed_on)
                self.assertTrue(any("canonical reviewed_on" in e for e in MODULE.validate(bad, self.nomenclature, self.domain)))

    def test_source_schema_version_mismatch_is_rejected(self):
        bad = copy.deepcopy(self.links)
        bad["source_contracts"]["domain_composition"]["schema_version"] = 99
        self.assertTrue(any("domain_composition source schema_version mismatch" in e for e in MODULE.validate(bad, self.nomenclature, self.domain)))

    def test_every_link_has_non_equivalence_boundary(self):
        for item in self.links["links"]:
            self.assertTrue(item["basis"].strip())
            self.assertTrue(item["non_equivalence_note"].strip())

if __name__ == "__main__":
    unittest.main()
