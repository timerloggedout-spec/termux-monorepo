"""Model-access proof harness (monorepo issue #4534, live leg).

Proves the fleet's Gemini access drives the StudySprint Strands
agent end to end: construct the agent, swap its model to
GeminiModel(gemini-3.8-flash) BEFORE invocation, run the
fetch-syllabus -> make_plan prompt, and assert both tools were
actually called (tool_metrics), not merely registered.

Construction note (D1's finding of record on #4534): in
strands-agents 1.63.0, Agent() with no model eagerly constructs
a BedrockModel, so build_strands_agent() raises without AWS
credentials present. The workflow supplies LITERAL placeholder
AWS env vars so construction succeeds; no AWS call is ever made
-- the model is Gemini before the first invocation. This is
disclosed in the receipt, not hidden.

Output: strands-proof-receipt.json in the working directory
(the workflow uploads it as the run's artifact). Exit code is
non-zero on ANY failure, with the exact exception in the
receipt's "error" field when one exists -- the failure is the
deliverable in that case, undressed.
"""
from __future__ import annotations

import json
import os
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

PROMPT = (
    "Fetch the syllabus evidence for examples/syllabus.json using "
    "fetch_syllabus_evidence, then call make_plan with the fetched "
    "course JSON, then summarize the plan in one paragraph."
)
REQUIRED_TOOLS = ("fetch_syllabus_evidence", "make_plan")


def main() -> int:
    receipt: dict = {
        "proof": "studysprint-strands-model-access",
        "issue": 4534,
        "provider": "google-gemini via fleet Actions secret",
        "model": "gemini-3.8-flash",
        "strands_agent_available": False,
        "deployment": False,
        "construction_note": (
            "Agent() eagerly constructs BedrockModel in "
            "strands-agents 1.63.0; construction ran with "
            "literal placeholder AWS env vars (no AWS call is "
            "made); the model was swapped to GeminiModel before "
            "invocation."
        ),
        "tools_called": [],
    }
    try:
        import strands
        receipt["sdk"] = getattr(strands, "__version__", "unknown")
        from agent import build_strands_agent
        agent = build_strands_agent()
        if agent is None:
            raise RuntimeError("build_strands_agent() returned None "
                               "(SDK import failed inside agent.py)")
        receipt["strands_agent_available"] = True

        from strands.models.gemini import GeminiModel
        agent.model = GeminiModel(
            client_args={"api_key": os.environ["GEMINI_API_KEY"]},
            model_id="gemini-3.8-flash")

        result = agent(PROMPT)
        metrics = getattr(result, "metrics", None)
        tool_metrics = getattr(metrics, "tool_metrics", {}) or {}
        receipt["tools_called"] = sorted(tool_metrics.keys())
        missing = [t for t in REQUIRED_TOOLS
                   if t not in tool_metrics]
        if missing:
            raise AssertionError(
                f"required tools not called: {missing}; "
                f"tool_metrics keys: {receipt['tools_called']}")
        reply = str(getattr(result, "message", result))
        receipt["reply_excerpt"] = reply[:600]
        receipt["verdict"] = "PASS"
    except BaseException as exc:  # the exact failure IS the return
        receipt["verdict"] = "FAIL"
        receipt["error"] = f"{type(exc).__name__}: {exc}"
        receipt["traceback_tail"] = traceback.format_exc()[-1200:]
        Path("strands-proof-receipt.json").write_text(
            json.dumps(receipt, indent=2))
        print(json.dumps(receipt, indent=2))
        return 1
    Path("strands-proof-receipt.json").write_text(
        json.dumps(receipt, indent=2))
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
