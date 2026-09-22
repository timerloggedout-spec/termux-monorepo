import unittest

from scripts.system_one_adapters import (
    DecisionRequest,
    TypeSafeJevAdapter,
    UnavailableAdapter,
    engine_catalog,
    langchain_boundary,
)

class SystemOneAdapterTests(unittest.TestCase):
    def request(self):
        return DecisionRequest(state={"body":"x"}, questions={"route":{"type":"choice","criteria":{"a":"A","b":"B"}}}, experiment_id="exp", lane_id="C", category="routing")

    def test_unavailable_adapter_is_explicit(self):
        result=UnavailableAdapter().evaluate(self.request())
        self.assertEqual(result.status,"UNAVAILABLE")
        self.assertEqual(result.metadata["failure_class"],"ENGINE_UNAVAILABLE")

    def test_jev_without_key_is_unavailable_not_failed(self):
        result=TypeSafeJevAdapter(api_key=None).evaluate(self.request())
        self.assertEqual(result.status,"UNAVAILABLE")
        self.assertEqual(result.metadata["failure_class"],"ENGINE_UNAVAILABLE")

    def test_category_catalog_is_extensible(self):
        catalog=engine_catalog()
        self.assertIn("laya",catalog)
        self.assertIn("jev",catalog)
        self.assertIn("security",catalog["jev"]["categories"])

    def test_langchain_boundary_has_no_execution_authority(self):
        boundary=langchain_boundary()
        self.assertIn("adapter only",boundary["execution"])
        self.assertIn("no provider command",boundary["authority"])

if __name__=="__main__":
    unittest.main()
