"""Synthetic, deterministic tests only; no live task cohort is included."""
import unittest
from scripts.model_selection_market.dspy_doe import DoeArm, LiveTaskDoe

class LiveDoeTests(unittest.TestCase):
    def make(self, **kw):
        options = dict(contexts=["termux-development"], hypotheses={"termux-development": "candidate improves PASS rate"},
            metric="task-pass", meaningful_effect=.2, planned_looks=[2], sample_cap=4, alpha=.05,
            power_target=.8, treatment_order_seed=17, control=DoeArm("A", "control"), candidate=DoeArm("B", "candidate"))
        options.update(kw)
        return LiveTaskDoe(**options)

    def record(self, doe, unit, arm, outcome, attempt=1, repetition=1):
        return doe.record_task(task_url=f"https://example.test/{unit}", source_snapshot_hash="a"*64,
            task_contract_hash="b"*64, context="termux-development", task_unit_id=unit,
            repetition=repetition, attempt=attempt, source_sha="c"*40, arm_id=arm, outcome=outcome)

    def test_exact_paired_and_retries_are_not_independent(self):
        d = self.make()
        for unit in ("one", "two"):
            self.record(d, unit, "A", "FAIL")
            self.record(d, unit, "B", "PASS")
        out = d.analyze(look=2)["contexts"]["termux-development"]
        self.assertEqual(out["eligible_pairs"], 2)
        self.assertEqual(out["discordant_wins"], 2)
        self.assertEqual(out["exact_two_sided_p"], .5)
        self.assertIsNone(out["winner"])
        self.assertEqual(out["interval"], None)
        with self.assertRaises(ValueError): self.record(d, "one", "B", "PASS")
        self.record(d, "one", "B", "PASS", attempt=2)
        self.assertEqual(d.analyze(look=2)["contexts"]["termux-development"]["censored_pairs"], 1)

    def test_censored_and_unpaired_cannot_claim(self):
        d = self.make()
        self.record(d, "x", "A", "UNKNOWN")
        self.record(d, "x", "B", "PASS")
        self.record(d, "y", "A", "FAIL")
        out = d.analyze(look=2)["contexts"]["termux-development"]
        self.assertEqual(out["eligible_pairs"], 0)
        self.assertEqual(out["censored_pairs"], 1)
        self.assertEqual(out["incomplete_pairs"], 1)
        self.assertIsNone(out["winner"])

    def test_task_effect_denominator_includes_ties(self):
        d = self.make(planned_looks=[99], sample_cap=99)
        for n in range(99):
            self.record(d, str(n), "A", "FAIL" if n < 9 else "PASS")
            self.record(d, str(n), "B", "PASS")
        out = d.analyze(look=99)["contexts"]["termux-development"]
        self.assertEqual(out["discordant_wins"], 9)
        self.assertEqual(out["tie_pairs"], 90)
        self.assertAlmostEqual(out["task_level_effect"], 9/99)

    def test_screening_never_claims_winner(self):
        d = self.make(screening=True)
        for unit in ("a", "b"):
            self.record(d, unit, "A", "FAIL")
            self.record(d, unit, "B", "PASS")
        self.assertIsNone(d.analyze(look=2)["contexts"]["termux-development"]["winner"])

    def test_requires_hashes_context_and_prespecified_look(self):
        d = self.make()
        with self.assertRaises(ValueError):
            d.record_task(task_url="", source_snapshot_hash="a"*64, task_contract_hash="b"*64, context="termux-development",
                task_unit_id="x", repetition=1, attempt=1, source_sha="c"*40, arm_id="A", outcome="PASS")
        with self.assertRaises(ValueError): d.analyze(look=1)
        with self.assertRaises(ValueError): self.make(contexts=["other"])
        for rep, att in ((True, 1), (1, False)):
            with self.assertRaises(ValueError): self.record(d, "bad", "A", "PASS", repetition=rep, attempt=att)

    def test_declared_look_rejects_future_observation_overrun_and_plan_is_copy(self):
        d = self.make()
        plan = d.plan
        plan["planned_looks"].append(8)
        self.assertEqual(d.plan["planned_looks"], [2])
        self.record(d, "a", "A", "FAIL")
        self.record(d, "a", "B", "PASS")
        self.record(d, "b", "A", "FAIL")
        self.record(d, "b", "B", "PASS")
        self.record(d, "c", "A", "FAIL")
        self.record(d, "c", "B", "PASS")
        with self.assertRaises(ValueError): d.analyze(look=8)
        with self.assertRaises(ValueError): d.analyze(look=2)

    def test_one_source_cannot_be_aliased_or_changed_between_arms(self):
        d = self.make()
        self.record(d, 'one', 'A', 'FAIL')
        values = dict(task_url='https://example.test/one', source_snapshot_hash='a' * 64,
            task_contract_hash='b' * 64, context='termux-development', task_unit_id='alias',
            repetition=1, attempt=1, source_sha='c' * 40, arm_id='B', outcome='PASS')
        with self.assertRaises(ValueError): d.record_task(**values)
        values.update(task_unit_id='one', source_snapshot_hash='d' * 64)
        with self.assertRaises(ValueError): d.record_task(**values)

if __name__ == "__main__":
    unittest.main()
