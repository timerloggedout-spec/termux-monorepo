"""Offline tests for Ballet choreography and DoE integration."""
import pathlib, sys, tempfile, unittest
HERE = pathlib.Path(__file__).resolve()
for parent in [HERE.parent, *HERE.parents]:
    if (parent / "deepcli" / "observatory").is_dir():
        sys.path.insert(0, str(parent)); break
from deepcli.observatory.ballet import plan_choreography, score_observation, run_doe_tournament
from deepcli.observatory.leaderboard import Leaderboard

TASKS = [
 {"id":"spec","depends_on":[],"writes":["spec.md"],"estimated_duration_ms":10},
 {"id":"tests","depends_on":["spec"],"writes":["tests.py"],"estimated_duration_ms":20},
 {"id":"docs","depends_on":["spec"],"writes":["docs.md"],"estimated_duration_ms":15},
 {"id":"integrate","depends_on":["tests","docs"],"writes":["release"],"estimated_duration_ms":5},
]
class TestBalletPlanner(unittest.TestCase):
 def test_sequential(self):
  p=plan_choreography(TASKS,"sequential"); self.assertEqual(p["wave_count"],4)
 def test_parallel_siblings(self):
  self.assertEqual(plan_choreography(TASKS,"parallel")["waves"],
                   [["spec"],["docs","tests"],["integrate"]])
 def test_write_conflict_serialized(self):
  p=plan_choreography([{"id":"a","writes":["x"]},{"id":"b","writes":["x"]}],"parallel")
  self.assertEqual(p["wave_count"],2)
 def test_capacity(self):
  self.assertEqual(plan_choreography(TASKS,"adaptive",1)["wave_count"],4)
 def test_invalid_graphs(self):
  with self.assertRaises(ValueError): plan_choreography([{"id":"a","depends_on":["missing"]}])
  with self.assertRaises(ValueError): plan_choreography([{"id":"a","depends_on":["b"]},{"id":"b","depends_on":["a"]}])
 def test_non_parallel_safe(self):
  p=plan_choreography([{"id":"unsafe","parallel_safe":False},{"id":"safe"}],"parallel")
  self.assertEqual(p["waves"],[["safe"],["unsafe"]])
class TestBalletEvaluation(unittest.TestCase):
 def observation(self):
  return {"accepted":True,"integrated_correctness":True,"time_to_integration_ms":1000,
   "cost_usd":0.1,"retries":0,"conflicts":0,"duplicate_actions":0,"human_interventions":0,
   "baselines":{"time_to_integration_ms":10000,"cost_usd":1.0}}
 def test_score_version_and_components(self):
  s=score_observation(self.observation()); self.assertEqual(s["score_version"],"ballet.moneyball.v1")
  self.assertEqual(s["components"]["correctness"],1.0)
 def test_missing_evidence_rejected(self):
  with self.assertRaises(ValueError): score_observation({"accepted":True})
 def test_tournament_uses_repo_framework(self):
  obs={f"{s}-cap{n}":self.observation() for s in ("sequential","parallel","adaptive") for n in (1,2,4)}
  lb=Leaderboard(pathlib.Path(tempfile.mkdtemp())/"lb.json")
  result=run_doe_tournament(TASKS,obs,leaderboard=lb)
  self.assertEqual(len(result["arms"]),9)
  self.assertEqual(len(result["tournament"]["winners"]),3)
if __name__=="__main__": unittest.main()
