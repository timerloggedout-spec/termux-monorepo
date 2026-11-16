import json
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACTION = ROOT / ".github/actions/http-llm-invoke/action.yml"
INPUT_FILTER = '(.usage? // {}) as $u | ($u.prompt_tokens // $u.input_tokens) as $v | if ($v | type) == "number" and $v >= 0 and ($v | floor) == $v then $v else null end'
OUTPUT_FILTER = '(.usage? // {}) as $u | ($u.completion_tokens // $u.output_tokens) as $v | if ($v | type) == "number" and $v >= 0 and ($v | floor) == $v then $v else null end'


class HttpLlmInvokeUsageContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.action = ACTION.read_text(encoding="utf-8")

    def test_missing_token_usage_is_preserved_as_json_null(self):
        self.assertIn("TOKENS_IN_JSON=", self.action)
        self.assertIn("TOKENS_OUT_JSON=", self.action)
        self.assertIn(INPUT_FILTER, self.action)
        self.assertIn(OUTPUT_FILTER, self.action)
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

    @unittest.skipUnless(shutil.which("jq"), "jq is required to exercise the producer filter")
    def test_input_usage_distinguishes_missing_zero_and_invalid(self):
        cases = [
            ({}, None),
            ({"usage": {"prompt_tokens": 0}}, 0),
            ({"usage": {"input_tokens": 17}}, 17),
            ({"usage": {"prompt_tokens": -1}}, None),
            ({"usage": {"prompt_tokens": 1.5}}, None),
            ({"usage": {"prompt_tokens": "17"}}, None),
        ]
        for payload, expected in cases:
            with self.subTest(payload=payload):
                result = subprocess.run(
                    ["jq", "-c", INPUT_FILTER],
                    input=json.dumps(payload),
                    capture_output=True,
                    text=True,
                    check=True,
                )
                self.assertEqual(json.loads(result.stdout), expected)

    @unittest.skipUnless(shutil.which("jq"), "jq is required to exercise the producer filter")
    def test_output_usage_distinguishes_missing_zero_and_invalid(self):
        cases = [
            ({}, None),
            ({"usage": {"completion_tokens": 0}}, 0),
            ({"usage": {"output_tokens": 9}}, 9),
            ({"usage": {"completion_tokens": -1}}, None),
            ({"usage": {"completion_tokens": 2.5}}, None),
        ]
        for payload, expected in cases:
            with self.subTest(payload=payload):
                result = subprocess.run(
                    ["jq", "-c", OUTPUT_FILTER],
                    input=json.dumps(payload),
                    capture_output=True,
                    text=True,
                    check=True,
                )
                self.assertEqual(json.loads(result.stdout), expected)


if __name__ == "__main__":
    unittest.main()
