import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "delphi"))
sys.path.insert(0, str(ROOT / "scripts" / "qdesk"))

from proposal_package import build_manifest
from award_authorization import (
    WorkPacketHeld, authorize_work_packet, require_work_packet_authorization,
)


class TestQDeskAwardAuthorization(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "RFP.md").write_text("# Proposal\n", encoding="utf-8")
        (self.root / "ITEMS.md").write_text("# Items\n", encoding="utf-8")
        self.manifest = build_manifest(
            source_ref="a" * 40,
            package_id="qdesk-authorization-test",
            package_path="docs/proposals/qdesk-authorization-test",
            package_author="builder",
            root=self.root,
            files=["RFP.md", "ITEMS.md"],
        )
        self.ledger_ref = "issue-comment:99"
        self.award = {
            "package_digest": self.manifest["package_digest"],
            "decision": "shadow",
            "ledger_ref": self.ledger_ref,
            "reviewer_login": "reviewer",
        }
        self.ledger = {**self.award}
        self.ledger["ledger_ref"] = self.ledger_ref

    def tearDown(self):
        self.temp.cleanup()

    def kwargs(self):
        return {
            "manifest": self.manifest,
            "award": self.award,
            "package_root": self.root,
            "checkout_sha": "a" * 40,
            "authenticated_package_author": "builder",
            "authenticated_reviewer": "reviewer",
            "ledger_lookup": lambda ref: self.ledger if ref == self.ledger_ref else None,
        }

    def test_exact_package_and_canonical_independent_award_authorize(self):
        result = authorize_work_packet(**self.kwargs())
        self.assertEqual(result["disposition"], "AUTHORIZED")
        self.assertEqual(result["package_digest"], self.manifest["package_digest"])
        self.assertEqual(result["reviewer_login"], "reviewer")
        self.assertEqual(require_work_packet_authorization(**self.kwargs()), result)

    def test_missing_ledger_lookup_fails_closed(self):
        args = self.kwargs()
        args["ledger_lookup"] = None
        result = authorize_work_packet(**args)
        self.assertEqual(result["disposition"], "HELD")
        with self.assertRaises(WorkPacketHeld):
            require_work_packet_authorization(**args)

    def test_author_impersonation_and_self_review_fail_closed(self):
        args = self.kwargs()
        args["authenticated_package_author"] = "attacker"
        self.assertEqual(authorize_work_packet(**args)["disposition"], "HELD")
        args = self.kwargs()
        args["authenticated_reviewer"] = "builder"
        self.assertEqual(authorize_work_packet(**args)["disposition"], "HELD")

    def test_package_drift_and_checkout_mismatch_fail_closed(self):
        args = self.kwargs()
        (self.root / "RFP.md").write_text("# Changed\n", encoding="utf-8")
        self.assertEqual(authorize_work_packet(**args)["disposition"], "HELD")
        (self.root / "RFP.md").write_text("# Proposal\n", encoding="utf-8")
        args = self.kwargs()
        args["checkout_sha"] = "b" * 40
        self.assertEqual(authorize_work_packet(**args)["disposition"], "HELD")

    def test_fabricated_ledger_reference_fails_closed(self):
        args = self.kwargs()
        args["award"] = {**self.award, "ledger_ref": "issue-comment:does-not-exist"}
        self.assertEqual(authorize_work_packet(**args)["disposition"], "HELD")


if __name__ == "__main__":
    unittest.main()
