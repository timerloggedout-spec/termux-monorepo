import unittest
from ml.pipelines.lanes.supersede_rules import should_supersede

class SupersedeTest(unittest.TestCase):
    def test_stamp(self) -> None:
        self.assertTrue(should_supersede({"title": "ops(skills): stamp evidence-led cycle"}))
    def test_product_fresh(self) -> None:
        self.assertFalse(should_supersede({"title": "feat(ml): keep-alive", "age_days": 1, "product": True}))

if __name__ == "__main__":
    unittest.main()
