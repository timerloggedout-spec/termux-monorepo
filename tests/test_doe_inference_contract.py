import copy
import json
import unittest
from pathlib import Path

from scripts.ci.check_doe_inference_contract import validate_contract

ROOT = Path(__file__).resolve().parents[1]

class DoEInferenceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.feed = json.loads((ROOT / "ops/challenge/desk-feed.json").read_text())
        cls.design = json.loads((ROOT / "experiments/doe/util-1-provider-rotation/DESIGN.json").read_text())
        cls.schema = json.loads((ROOT / "docs/schemas/inference-selection-receipt.schema.json").read_text())
        cls.roster = (ROOT / "docs/ops/SCOUT-ROSTER.md").read_text()
        cls.missions = (ROOT / "docs/ops/SCOUT-MISSIONS.md").read_text()
        cls.gambling = (ROOT / "docs/ops/AGENTIC-GAMBLING-LANE.md").read_text()

    def validate(self, feed=None):
        return validate_contract(feed or self.feed, self.design, self.schema,
                                 self.roster, self.missions, self.gambling)

    def test_current_contract_is_consistent(self):
        self.assertEqual([], self.validate())

    def test_legacy_no_repeat_rule_cannot_become_active_again(self):
        feed = copy.deepcopy(self.feed)
        feed["dispatch"]["provider_catalog"]["rotation_rule"]["rule"] += " No provider takes 2 consecutive dispatches."
        self.assertTrue(any("superseded consecutive-provider rule" in e for e in self.validate(feed)))

    def test_desk_cannot_claim_allocation_authority(self):
        feed = copy.deepcopy(self.feed)
        feed["dispatch"]["provider_catalog"]["rotation_rule"]["rule"] = "Desk owns allocation."
        self.assertTrue(any("DoE as allocation/rotation authority" in e for e in self.validate(feed)))

if __name__ == "__main__":
    unittest.main()
