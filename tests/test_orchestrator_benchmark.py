import unittest
from scripts.ci.evaluate_orchestrator_benchmark import evaluate_case

class OrchestratorBenchmarkTests(unittest.TestCase):
    def case(self):
        return {
            "case_id":"boundary-001", "requires_abstain":True, "abstain_option_available":True,
            "wrong_commit_penalty":0.2, "required_fragments":{"actor":["f1","f2"],"critic":["f3"]},
            "distractors":{"actor":["private-critic-test"],"critic":["actor-private-context"]},
            "spawn_mode":"SPAWN", "actor_critic":True,
            "execution":{"exit_code":0,"assertions":["state_valid"],"state_change":True},
        }
    def observed(self):
        return {
            "routed_context":{"actor":["f1","f2"],"critic":["f3"]},
            "spawn_mode":"SPAWN","inherit_parent_context":False,"sibling_context_visible":False,
            "critic_private_context_visible_to_actor":False,"actor_context_visible_to_critic":True,
            "execution":{"exit_code":0,"assertions_passed":["state_valid"],"state_change":True},
            "wrong_commits":0,
        }
    def test_pass_and_boundary_failure(self):
        self.assertEqual(evaluate_case(self.case(),self.observed())["outcome"],"PASS")
        bad=self.observed(); bad["routed_context"]["actor"].append("private-critic-test")
        result=evaluate_case(self.case(),bad)
        self.assertEqual(result["outcome"],"FAIL_DETERMINISTIC")
        self.assertIn("actor:distractor_leak",result["failures"])
    def test_missing_fragment_fails(self):
        bad=self.observed(); bad["routed_context"]["critic"]=[]
        self.assertEqual(evaluate_case(self.case(),bad)["outcome"],"FAIL_DETERMINISTIC")
    def test_wrong_commit_penalty(self):
        bad=self.observed(); bad["wrong_commits"]=1
        result=evaluate_case(self.case(),bad)
        self.assertEqual(result["wrong_commit_penalty"],0.2); self.assertEqual(result["net_score"],0.8)
    def test_deterministic_failure_blocks_judge(self):
        bad=self.observed(); bad["execution"]["exit_code"]=1; bad["judge_score"]=1.0; bad["judge_weight"]=0.3
        result=evaluate_case(self.case(),bad)
        self.assertEqual(result["outcome"],"FAIL_DETERMINISTIC"); self.assertIsNone(result["judge_score"])
    def test_judge_only_on_inconclusive_and_capped(self):
        case=self.case(); case.pop("execution")
        obs=self.observed(); obs.pop("execution"); obs["judge_score"]=0.5; obs["judge_weight"]=0.3
        result=evaluate_case(case,obs)
        self.assertEqual(result["outcome"],"INCONCLUSIVE"); self.assertEqual(result["judge_weight"],0.3)
        obs["judge_weight"]=0.9; result=evaluate_case(case,obs)
        self.assertEqual(result["outcome"],"FAIL_DETERMINISTIC")
    def test_spawn_parent_inheritance_fails(self):
        bad=self.observed(); bad["inherit_parent_context"]=True
        result=evaluate_case(self.case(),bad)
        self.assertEqual(result["outcome"],"FAIL_DETERMINISTIC"); self.assertIn("parent_context_inherited",result["failures"])

if __name__ == "__main__": unittest.main()