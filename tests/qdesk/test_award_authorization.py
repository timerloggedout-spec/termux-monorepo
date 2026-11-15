import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "delphi"))
sys.path.insert(0, str(ROOT / "scripts" / "qdesk"))

from proposal_package import build_manifest
from scripts.delphi import gate
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

    def test_non_object_manifest_holds_at_qdesk_boundary(self):
        for malformed in (None, [], "not-an-object"):
            args = self.kwargs()
            args["manifest"] = malformed
            result = authorize_work_packet(**args)
            self.assertEqual(result["disposition"], "HELD")
            with self.assertRaises(WorkPacketHeld):
                require_work_packet_authorization(**args)




    def test_qdesk_uses_the_delphi_gate_canonical_comment_resolver(self):
        ledger_ref = gate.delphi_ledger_ref(8123)
        self.award["ledger_ref"] = ledger_ref
        self.ledger = {
            "ledger_ref": ledger_ref,
            "package_digest": self.manifest["package_digest"],
            "decision": "shadow",
            "reviewer_login": "reviewer",
        }
        record = {
            "input_hash": "abc123",
            "award": dict(self.ledger),
        }
        fence = chr(96) * 3
        body = gate.LEDGER_MARK + "\n" + fence + "json\n" + json.dumps(record) + "\n" + fence

        class FakeGH:
            repo = "timerloggedout-spec/termux-monorepo"
            def __init__(self):
                self.calls = []
            def req(self, method, path, body=None):
                self.calls.append((method, path))
                if path == "/issues/comments/8123":
                    return {
                        "id": 8123,
                        "issue_url": "https://api.github.com/repos/timerloggedout-spec/termux-monorepo/issues/5156",
                        "user": {"type": "Bot", "login": "github-actions[bot]"},
                        "body": body_text,
                    }
                if path == "/issues/5156/comments?per_page=100&page=1":
                    return [{
                        "id": 8123,
                        "user": {"type": "Bot", "login": "github-actions[bot]"},
                        "body": body_text,
                    }]
                raise AssertionError(f"unexpected GitHub request: {path}")

        body_text = body
        fake = FakeGH()
        args = self.kwargs()
        args["ledger_lookup"] = lambda ref: gate.lookup_delphi_ledger_record(fake, ref)
        self.assertEqual(authorize_work_packet(**args)["disposition"], "AUTHORIZED")
        self.assertEqual(fake.calls, [
            ("GET", "/issues/comments/8123"),
            ("GET", "/issues/5156/comments?per_page=100&page=1"),
        ])


if __name__ == "__main__":
    unittest.main()
