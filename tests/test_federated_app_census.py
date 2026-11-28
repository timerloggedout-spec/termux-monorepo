import copy, json, unittest
from pathlib import Path
from scripts.validate_federated_app_census import validate
ROOT=Path(__file__).resolve().parents[1]
class FederatedAppCensusTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data=json.loads((ROOT/"docs/ops/federated-app-repository-census.json").read_text())
 def test_checked_in_census_is_valid(self): self.assertEqual(validate(self.data),[])
 def test_duplicate_repository_is_rejected(self):
  d=copy.deepcopy(self.data); d["repositories"].append(copy.deepcopy(d["repositories"][0]))
  self.assertTrue(any("duplicate repository" in e for e in validate(d)))
 def test_count_mismatch_is_rejected(self):
  d=copy.deepcopy(self.data); d["source"]["unique_repositories"]+=1
  self.assertTrue(any("does not match" in e for e in validate(d)))
 def test_candidate_must_exist_in_census(self):
  d=copy.deepcopy(self.data); d["application_review_queue"][0]["repository"]="timerloggedout-spec/not-real"
  self.assertTrue(any("absent from census" in e for e in validate(d)))
 def test_no_product_id_is_invented(self):
  d=copy.deepcopy(self.data); d["repositories"][0]["product_app_id"]="app-123"
  self.assertTrue(any("cannot invent" in e for e in validate(d)))
if __name__=="__main__": unittest.main()
