"""AWS Lambda packaging for the entry agent.

The handler is the deployable unit the Strands Decider agent invokes
(the Decider pattern targets Amazon Bedrock; the tool ships as a Lambda
function). It is deliberately dependency-free: the same handler runs
locally for the completion record — event in, receipt out — because no
AWS account exists (owner card rule) and the entry claims no live AWS
deployment.

Event shape:
    {"request": {"id": str, "action": str, "risk_tier": str,
                 "asserted": bool,
                 "artifact": {"kind": ..., "ref": ...} | absent}}
Response shape: {"statusCode": 200, "body": <receipt JSON string>}
"""

from __future__ import annotations

import json

from agent import run_agent


def handler(event, context=None):
    request = event["request"] if "request" in event else event
    receipt = run_agent(request)
    return {"statusCode": 200, "body": json.dumps(receipt)}


if __name__ == "__main__":  # local smoke: asserted-only request -> ABSTAIN
    out = handler({"request": {"id": "smoke", "action": "inspect",
                               "asserted": True}})
    print(out["statusCode"], json.loads(out["body"])["decision_final"])
