import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACTION = ROOT / ".github/actions/http-llm-invoke/action.yml"


class HttpLlmInvokeUsageContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.action = ACTION.read_text(encoding="utf-8")

    def test_missing_token_usage_is_preserved_as_json_null(self):
        self.assertIn("TOKENS_IN_JSON=", self.action)
        self.assertIn("TOKENS_OUT_JSON=", self.action)
        self.assertIn("then $v else null end", self.action)
        self.assertIn('--argjson tokens_in "${TOKENS_IN_JSON:-null}"', self.action)
        self.assertIn('--argjson tokens_out "${TOKENS_OUT_JSON:-null}"', self.action)
        self.assertNotIn(".usage.prompt_tokens // .usage.input_tokens // 0", self.action)
        self.assertNotIn(".usage.completion_tokens // .usage.output_tokens // 0", self.action)

    def test_numeric_fallback_is_confined_to_completion_cap_detection(self):
        self.assertIn("TOKENS_IN_NUM=", self.action)
        self.assertIn("TOKENS_OUT_NUM=", self.action)
        self.assertIn('[ "$TOKENS_OUT_NUM" -ge "$MAX_TOKENS" ]', self.action)
        self.assertIn("tokens_in:$tokens_in,tokens_out:$tokens_out", self.action)
        self.assertNotIn("tokens_in:$TOKENS_IN_NUM", self.action)
        self.assertNotIn("tokens_out:$TOKENS_OUT_NUM", self.action)


if __name__ == "__main__":
    unittest.main()
