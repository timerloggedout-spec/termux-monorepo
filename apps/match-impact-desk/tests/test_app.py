import os, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import app

class MatchTests(unittest.TestCase):
    def test_clean_invoice(self):
        a=app.analyze(app.SEED[0]); self.assertEqual(a["match_status"],"matched"); self.assertEqual(a["invoice_total"],"1360.00")
    def test_amended_po_price_delta(self):
        a=app.analyze(app.SEED[1]); self.assertEqual(a["disposition"],"credit_memo"); self.assertEqual(a["impact"]["exposure"],"50.00")
    def test_duplicate_blocks_full_invoice(self):
        a=app.analyze(app.SEED[2]); self.assertEqual(a["disposition"],"block"); self.assertEqual(a["impact"]["exposure"],"1150.00")
    def test_short_receipt_is_held(self):
        a=app.analyze(app.SEED[3]); self.assertEqual(a["disposition"],"hold"); self.assertEqual(a["impact"]["exposure"],"800.00")

class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.p=patch.object(app,"DB",Path(self.tmp.name)/"test.db"); self.p.start(); app.initialize()
    def tearDown(self): self.p.stop(); self.tmp.cleanup()
    def test_seed_chain_is_valid(self): self.assertTrue(app.verify_chain()["valid"])
    def test_payment_actions_are_never_authorized_by_analysis(self):
        for case in app.SEED:
            self.assertIn("payment_release",app.analyze(case)["impact"]["blocked"])
            self.assertIn("ledger_posting",app.analyze(case)["impact"]["blocked"])
    def test_validated_case_intake_contract(self):
        case=dict(app.SEED[0]); case["case_id"]="MID-NEW-01"
        self.assertEqual(app.validate_case(case)["case_id"],"MID-NEW-01")
    def test_invalid_case_id_rejected(self):
        case=dict(app.SEED[0]); case["case_id"]="../escape"
        with self.assertRaises(ValueError): app.validate_case(case)
    def test_audit_chain_extends_after_new_event(self):
        with app.db_session() as db: app.audit_append(db,"MID-2402","controller_brief_drafted","test",{"brief_sha256":"abc"})
        self.assertTrue(app.verify_chain()["valid"])
    def test_model_brief_has_deterministic_fallback(self):
        with patch.dict(os.environ,{"MATCHDESK_INFERENCE_BASE_URL":""}):
            case=app.SEED[1]
            case={**case,"analysis":app.analyze(case)}
            result=app.review_brief(case)
            self.assertEqual(result["provider"],"deterministic-fallback")
            self.assertIn("50.00",result["brief"])

class DecisionPolicyTests(unittest.TestCase):
    def test_duplicate_invoice_cannot_be_approved(self):
        with self.assertRaisesRegex(ValueError,"duplicate invoice cannot be approved"):
            app.validate_decision(app.analyze(app.SEED[2]),"approve","Reviewed the duplicate invoice and compared the source records.")
    def test_exception_approval_requires_substantive_note(self):
        with self.assertRaisesRegex(ValueError,"substantive resolution note"):
            app.validate_decision(app.analyze(app.SEED[1]),"approve","ok")
    def test_clean_match_can_be_approved_without_exception_note(self):
        app.validate_decision(app.analyze(app.SEED[0]),"approve","")

if __name__=="__main__": unittest.main()
