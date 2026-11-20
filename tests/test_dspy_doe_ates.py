import unittest
from scripts.model_selection_market.dspy_doe import CollaboratorTreatment, DoeArm, DspyDoeStub

class DspyDoeIntegrationTests(unittest.TestCase):
    def test_benchmark_result_is_recorded_without_weight_mutation(self):
        stub=DspyDoeStub(); arm=DoeArm(arm_id="A",signature="triage_v1",factors={"routing":"delegated","actor_critic":"on"})
        result={"outcome":"PASS","deterministic_score":1.0,"judge_score":None,"judge_weight":0.0,"net_score":1.0,"wrong_commit_penalty":0.0}
        row=stub.record_benchmark_result(arm,result)
        self.assertTrue(row["not_default_router"]); self.assertEqual(row["metrics"]["outcome"],"PASS"); self.assertEqual(row["factors"]["routing"],"delegated")
        self.assertNotIn("weight",row)

    def test_collaborator_configuration_is_pinned_per_run(self):
        stub = DspyDoeStub()
        treatment = CollaboratorTreatment(
            collaborator_id="jules", moniker="h3yVern", role_revision="implementation/v2",
            profile_revision="3", persona_fingerprint="sha256:persona",
            execution_fingerprint="sha256:execution", configuration_fingerprint="sha256:config",
            source_record_refs=["muse-side-chat/2026-11-18:record-1"],
        )
        row = stub.run_arm(DoeArm(arm_id="B", signature="identity-v1"), collaborator=treatment, provider="google", adapter="jules-app")
        self.assertEqual(row["collaborator"]["collaborator_id"], "jules")
        self.assertEqual(row["collaborator"]["configuration_fingerprint"], "sha256:config")
        self.assertEqual(row["provider"], "google")
        self.assertEqual(row["adapter"], "jules-app")

    def test_unknown_collaborator_fields_remain_null(self):
        row = DspyDoeStub().run_arm(DoeArm(arm_id="C", signature="unknown"))
        self.assertIsNone(row["collaborator"]["collaborator_id"])
        self.assertIsNone(row["collaborator"]["persona_fingerprint"])

if __name__ == "__main__": unittest.main()