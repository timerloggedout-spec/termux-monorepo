"""Offline tests for Ballet choreography and receipt-backed DoE."""
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

def receipt(cohort, run):
    return {"source":"ATES","run_id":run,"cohort_id":cohort,
            "evidence_ref":f"ates://receipts/{run}","sha256":"a"*64}

def resolver_for(observations):
    receipts = {value["receipt"]["evidence_ref"]: value["receipt"] for value in observations.values()}
    return lambda evidence_ref: receipts[evidence_ref]

class TestBalletPlanner(unittest.TestCase):
 def test_sequential(self):
  p=plan_choreography(TASKS,"sequential"); self.assertEqual(p["wave_count"],4)
 def test_parallel_siblings(self):
  self.assertEqual(plan_choreography(TASKS,"parallel")["waves"],[["spec"],["docs","tests"],["integrate"]])
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
 def observation(self, cohort, run):
  return {"accepted":True,"integrated_correctness":True,"time_to_integration_ms":1000,
   "cost_usd":0.1,"retries":0,"conflicts":0,"duplicate_actions":0,"human_interventions":0,
   "baselines":{"time_to_integration_ms":10000,"cost_usd":1.0},"receipt":receipt(cohort,run)}
 def test_score_version_and_components(self):
  s=score_observation(self.observation("cohort-a","run-1"))
  self.assertEqual(s["score_version"],"ballet.moneyball.v2")
  self.assertEqual(s["components"]["correctness"],1.0)
 def test_metric_only_observation_rejected(self):
  with self.assertRaises(ValueError): score_observation({"accepted":True})
 def test_missing_receipt_fields_rejected(self):
  obs=self.observation("cohort-a","run-1"); obs["receipt"]={"source":"ATES"}
  with self.assertRaises(ValueError): score_observation(obs)
 def test_non_finite_metrics_rejected(self):
  observation=self.observation("cohort-a","run-1"); observation["cost_usd"]=float("nan")
  with self.assertRaises(ValueError): score_observation(observation)
 def test_tournament_uses_cohort_local_leaderboard(self):
  cohort="cohort-a"
  obs={f"{s}-cap{n}":self.observation(cohort,f"run-{s}-{n}") for s in ("sequential","parallel","adaptive") for n in (1,2,4)}
  lb=Leaderboard(pathlib.Path(tempfile.mkdtemp())/"lb.json")
  result=run_doe_tournament(TASKS,obs,leaderboard=lb,cohort_id=cohort,receipt_resolver=resolver_for(obs))
  winners=result["tournament"]["winners"]; losers=result["tournament"]["losers"]
  self.assertEqual(len(result["arms"]),9)
  self.assertEqual(len(winners),3)
  self.assertEqual(len(losers),3)
  self.assertTrue({(x["provider"],x["model"]) for x in winners}.isdisjoint({(x["provider"],x["model"]) for x in losers}))
 def test_distinct_treatments_have_distinct_arm_receipts(self):
  cohort="cohort-b"
  factors={"strategy":["parallel"],"max_parallel":[1],"collector_timing_policy":["event-driven","periodic"]}
  obs={
   "parallel-cap1__collector-timing-policy-event-driven":self.observation(cohort,"event-run"),
   "parallel-cap1__collector-timing-policy-periodic":self.observation(cohort,"periodic-run"),
  }
  result=run_doe_tournament(TASKS,obs,factors=factors,cohort_id=cohort,receipt_resolver=resolver_for(obs))
  self.assertEqual(len(result["arms"]),2)
  self.assertEqual(len(set(result["plans"])),2)
 def test_reused_leaderboard_separates_cohorts(self):
  lb=Leaderboard(pathlib.Path(tempfile.mkdtemp())/"lb.json")
  cohort_a="cohort-a"
  obs_a={f"{s}-cap{n}":self.observation(cohort_a,f"run-a-{s}-{n}") for s in ("sequential","parallel","adaptive") for n in (1,2,4)}
  run_doe_tournament(TASKS,obs_a,leaderboard=lb,cohort_id=cohort_a,receipt_resolver=resolver_for(obs_a))
  cohort_b="cohort-b"
  obs_b={"sequential-cap1":self.observation(cohort_b,"run-b-sequential")}
  result=run_doe_tournament([{"id":"solo"}],obs_b,
      factors={"strategy":["sequential"],"max_parallel":[1]},
      task_family="orchestration",leaderboard=lb,cohort_id=cohort_b,receipt_resolver=resolver_for(obs_b))
  self.assertEqual(len(result["tournament"]["winners"]),1)
  self.assertEqual(result["tournament"]["winners"][0]["provider"],"sequential")
 def test_receipt_cohort_mismatch_rejected(self):
  obs={"sequential-cap1":self.observation("cohort-other","run-1")}
  with self.assertRaises(ValueError):
   run_doe_tournament([{"id":"solo"}],obs,
      factors={"strategy":["sequential"],"max_parallel":[1]},cohort_id="cohort-current",receipt_resolver=resolver_for(obs))
 def test_missing_receipt_resolver_rejected(self):
  cohort="cohort-c"
  obs={"sequential-cap1":self.observation(cohort,"run-c")}
  with self.assertRaises(ValueError):
   run_doe_tournament([{"id":"solo"}],obs,factors={"strategy":["sequential"],"max_parallel":[1]},cohort_id=cohort)
 def test_canonical_receipt_mismatch_rejected(self):
  cohort="cohort-d"
  obs={"sequential-cap1":self.observation(cohort,"run-d")}
  def altered(_):
   return {**obs["sequential-cap1"]["receipt"],"sha256":"b"*64}
  with self.assertRaises(ValueError):
   run_doe_tournament([{"id":"solo"}],obs,factors={"strategy":["sequential"],"max_parallel":[1]},cohort_id=cohort,receipt_resolver=altered)
 def test_unsupported_factor_rejected(self):
  with self.assertRaises(ValueError):
   run_doe_tournament(TASKS,{},factors={"mystery":["x"]},cohort_id="cohort-a")

if __name__=="__main__": unittest.main()
