import unittest

from scripts.system_one_adapters import DecisionRequest, UnavailableAdapter, langchain_boundary


class SystemOneAdapterTests(unittest.TestCase):
    def test_unavailable_adapter_is_explicit(self) -> None:
        request = DecisionRequest(
            state={"body": "x"},
            questions={"route": {"type": "choice"}},
            experiment_id="exp",
            lane_id="C",
        )
        result = UnavailableAdapter().evaluate(request)
        self.assertEqual(result.status, "UNAVAILABLE")
        self.assertEqual(result.metadata["failure_class"], "ENGINE_UNAVAILABLE")

    def test_langchain_boundary_has_no_execution_authority(self) -> None:
        boundary = langchain_boundary()
        self.assertIn("adapter only", boundary["execution"])
        self.assertIn("no provider command", boundary["authority"])


if __name__ == "__main__":
    unittest.main()
