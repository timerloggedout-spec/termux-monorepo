import unittest
from scripts.model_selection_market.dspy_doe import DoeArm, DspyDoeStub

class DspyDoeIntegrationTests(unittest.TestCase):
    def test_benchmark_result_is_recorded_without_weight_mutation(self):
        stub=DspyDoeStub(); arm=DoeArm(arm_id="A",signature="triage_v1",factors={"routing":"delegated","actor_critic":"on"})
        result={"outcome":"PASS","deterministic_score":1.0,"judge_score":None,"judge_weight":0.0,"net_score":1.0,"wrong_commit_penalty":0.0}
        row=stub.record_benchmark_result(arm,result)
        self.assertTrue(row["not_default_router"]); self.assertEqual(row["metrics"]["outcome"],"PASS"); self.assertEqual(row["factors"]["routing"],"delegated")
        self.assertNotIn("weight",row)

if __name__ == "__main__": unittest.main()