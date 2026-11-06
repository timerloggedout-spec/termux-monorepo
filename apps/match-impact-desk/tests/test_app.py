import tempfile, unittest
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
        for c in app.SEED:
            self.assertIn("payment_release",app.analyze(c)["impact"]["blocked"])
            self.assertIn("ledger_posting",app.analyze(c)["impact"]["blocked"])

if __name__=="__main__": unittest.main()
