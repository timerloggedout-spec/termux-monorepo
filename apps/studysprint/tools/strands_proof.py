"""Model-access proof harness (monorepo issue #4534, live leg).

Branch (a) R1 (owner escalation 2026-11-04: branch (a) is
MANDATORY -- no completion without live Strands on AWS): the
StudySprint Strands agent is driven by strands' BedrockModel --
Amazon Bedrock is the invocation provider, not a construction
side-effect. This replaces the GeminiModel swap, which stands as
a DEFECT of record (a Gemini invocation is not AWS proof, however
model-agnostic the harness is).

Staged state: code complete, only credentials missing. The model
id is a SLOT -- env STRANDS_MODEL_ID, filled verbatim at fire
time (Nova-class; the rank-1 pin of record is
us.amazon.nova-lite-v1:0, us-east-1). Nothing model-specific is
baked into this file.

Fail-closed pre-flight (spec addendum A1 discipline): before any
construction or invocation, the harness requires (a) the model
slot set and (b) real AWS credentials in env -- the literal
"placeholder" values the workflow carries for construction are
REJECTED. A failed pre-flight writes the receipt with
fail_closed=true and exits non-zero; no AWS call is attempted.

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
MODEL_ID = os.environ.get("STRANDS_MODEL_ID", "")
REGION = os.environ.get("AWS_REGION", "us-east-1")
PLACEHOLDER = "placeholder"


class PreflightError(RuntimeError):
    """Staging gate: required fire-time inputs are absent."""


def preflight_missing() -> list[str]:
    missing = []
    if not MODEL_ID:
        missing.append("STRANDS_MODEL_ID (model slot, verbatim at "
                       "fire time)")
    ak = os.environ.get("AWS_ACCESS_KEY_ID", "")
    sk = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
    if not ak or ak == PLACEHOLDER or not sk or sk == PLACEHOLDER:
        missing.append("real AWS credentials in env "
                       "(AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY; "
                       "literal placeholders are rejected)")
    return missing


def main() -> int:
    receipt: dict = {
        "proof": "studysprint-strands-model-access",
        "issue": 4534,
        "branch": "a-r1",
        "provider": "amazon-bedrock",
        "model": MODEL_ID or None,
        "region": REGION,
        "run": os.environ.get("GITHUB_RUN_ID"),
        "commit": os.environ.get("GITHUB_SHA"),
        "strands_agent_available": False,
        "deployment": False,
        "construction_note": (
            "BedrockModel is the invocation model (branch (a) R1). "
            "strands-agents 1.63.0's Agent() also eagerly constructs "
            "a default BedrockModel at build time; the harness swaps "
            "in the slotted BedrockModel before invocation. "
            "Pre-flight rejects absent/placeholder credentials, so "
            "no run of this harness can pass without live Bedrock."
        ),
        "tools_required": list(REQUIRED_TOOLS),
        "tools_called": [],
    }
    try:
        missing = preflight_missing()
        if missing:
            receipt["fail_closed"] = True
            raise PreflightError(
                "pre-flight (staged, awaiting fire inputs): "
                + "; ".join(missing))

        import strands  # noqa: F401
        # strands exposes no __version__ (runs 1-3 stamped
        # "unknown"); the version of record is the installed
        # distribution's metadata.
        from importlib.metadata import version as _dist_version
        try:
            receipt["sdk"] = f"strands-agents {_dist_version('strands-agents')}"
        except Exception:
            receipt["sdk"] = "unknown"
        from agent import build_strands_agent
        agent = build_strands_agent()
        if agent is None:
            raise RuntimeError("build_strands_agent() returned None "
                               "(SDK import failed inside agent.py)")
        receipt["strands_agent_available"] = True

        # A1 fail-fast transport: no IMDS (workflow env disables
        # it), short connect timeout, bounded read, few attempts --
        # a credential/transport failure surfaces as the receipt's
        # error, never as a stall.
        from botocore.config import Config as BotoConfig
        from strands.models.bedrock import BedrockModel
        agent.model = BedrockModel(
            model_id=MODEL_ID,
            region_name=REGION,
            boto_client_config=BotoConfig(
                connect_timeout=2,
                read_timeout=120,
                retries={"max_attempts": 2, "mode": "standard"}))

        result = agent(PROMPT)
        metrics = getattr(result, "metrics", None)
        tool_metrics = getattr(metrics, "tool_metrics", {}) or {}
        receipt["tools_called"] = sorted(tool_metrics.keys())
        missing_tools = [t for t in REQUIRED_TOOLS
                         if t not in tool_metrics]
        if missing_tools:
            raise AssertionError(
                f"required tools not called: {missing_tools}; "
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
