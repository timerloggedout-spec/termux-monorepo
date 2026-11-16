# %% [P1' STUDIO PROBE -- branch (a) R1, single drop + run]
"""P1' door probe: run INSIDE the AWS Studio session (post
GitHub-bound social sign-in, Free plan) and fire the R1 receipt
in-session.

Single file, drop + run top to bottom (notebook cells marked
# %%). Three cells, each independently recorded -- a failure in
one never hides the others:

  cell 1  sts:GetCallerIdentity        (whose account/role is this)
  cell 2  bedrock:ListFoundationModels (is Nova Lite on this acct)
  cell 3  1x Nova Lite invoke          (the live call)

Cell 3 prefers the Strands path (Agent + BedrockModel -- the R1
claim is live STRANDS on Bedrock). If strands is not importable
in the session it falls back to bedrock-runtime Converse and the
receipt stamps strands_used=false -- the substitution is a
first-class receipt field, never silent (the Gemini defect was a
silent swap; this one is on the face of the receipt).

Stamped risks this probe is built to surface precisely:
  * role may lack bedrock:InvokeModel -- cell 3's error record
    carries the exact exception type + message (the amend path
    starts from that string);
  * new-customer cohort limits -- cell 1 stamps the identity the
    session actually holds, so cohort/role surprises are visible.

Output: the receipt JSON printed + written to
strands-proof-receipt.json in the working directory.
Exit code 0 only when all three cells pass.
"""
import json
import os
import time
import traceback
from pathlib import Path

# %% [config]
MODEL_ID = os.environ.get("STRANDS_MODEL_ID", "us.amazon.nova-lite-v1:0")
REGION = os.environ.get("AWS_REGION", "us-east-1")
PROMPT = "Reply with one short sentence confirming you are live."

from botocore.config import Config as _BotoConfig

CFG = _BotoConfig(connect_timeout=3, read_timeout=60,
                  retries={"max_attempts": 1, "mode": "standard"})

receipt = {
    "proof": "studysprint-strands-model-access",
    "issue": 4534,
    "branch": "a-r1-p1prime-studio",
    "session": "aws-studio-p1prime",
    "provider": "amazon-bedrock",
    "model": MODEL_ID,
    "region": REGION,
    "deployment": False,
    "strands_used": None,
    "cells": {},
}

try:
    from importlib.metadata import version as _v
    receipt["boto3"] = _v("boto3")
    try:
        receipt["sdk"] = f"strands-agents {_v('strands-agents')}"
    except Exception:
        receipt["sdk"] = None
except Exception:
    receipt["boto3"] = None
    receipt["sdk"] = None


def run_cell(name, fn):
    t0 = time.time()
    try:
        out = fn()
        receipt["cells"][name] = {
            "ok": True, "latency_s": round(time.time() - t0, 2), **out}
    except BaseException as exc:
        receipt["cells"][name] = {
            "ok": False, "latency_s": round(time.time() - t0, 2),
            "error_type": type(exc).__name__, "error": str(exc)[:600]}
    print(f"cell {name}: ok={receipt['cells'][name]['ok']}")


# %% [cell 1 -- sts identity]
def cell_sts():
    import boto3
    ident = boto3.client("sts", region_name=REGION,
                         config=CFG).get_caller_identity()
    return {"account": ident.get("Account"), "arn": ident.get("Arn"),
            "user_id": ident.get("UserId")}


run_cell("sts_identity", cell_sts)

# %% [cell 2 -- list foundation models]
def cell_list():
    import boto3
    resp = boto3.client("bedrock", region_name=REGION,
                        config=CFG).list_foundation_models()
    ids = [m.get("modelId", "") for m in resp.get("modelSummaries", [])]
    nova = [i for i in ids if i.endswith("nova-lite-v1:0")]
    if not nova:
        raise RuntimeError(
            f"Nova Lite not in foundation model list ({len(ids)} "
            f"models); nova-family present: "
            f"{[i for i in ids if 'nova' in i][:8]}")
    return {"models_listed": len(ids), "nova_lite_ids": nova}


run_cell("list_foundation_models", cell_list)

# %% [cell 3 -- 1x Nova Lite invoke]
def cell_invoke():
    try:
        from strands import Agent
        from strands.models.bedrock import BedrockModel
    except ImportError:
        receipt["strands_used"] = False
        import boto3
        rt = boto3.client("bedrock-runtime", region_name=REGION,
                          config=CFG)
        resp = rt.converse(
            modelId=MODEL_ID,
            messages=[{"role": "user",
                       "content": [{"text": PROMPT}]}])
        text = resp["output"]["message"]["content"][0]["text"]
        return {"path": "boto3-converse (strands unavailable)",
                "reply_excerpt": text[:600]}
    receipt["strands_used"] = True
    agent = Agent(model=BedrockModel(
        model_id=MODEL_ID, region_name=REGION, boto_client_config=CFG))
    result = agent(PROMPT)
    return {"path": "strands Agent + BedrockModel",
            "reply_excerpt": str(getattr(result, "message", result))[:600]}


run_cell("invoke_nova_lite", cell_invoke)

# %% [receipt]
receipt["verdict"] = ("PASS" if all(c.get("ok")
                                   for c in receipt["cells"].values())
                      else "FAIL")
Path("strands-proof-receipt.json").write_text(
    json.dumps(receipt, indent=2))
print(json.dumps(receipt, indent=2))
raise SystemExit(0 if receipt["verdict"] == "PASS" else 1)
