#!/usr/bin/env python3
"""chat-intent v1 — rules-tier intent classification of owner chat
messages. Registered as a DoE method version (docs/ops/DOE-FAMILY.md,
rule 8): versioned, backfilled on version change, comparison line
continuous, cullable.

Classes: request · directive · aside · speculation · question.
Eval substrate = labeled chat outcomes (weak supervision: a message
whose outcome was built/routed vs discussed-only). No ESTABLISHED
accuracy claim until n>=30 labeled outcomes per class.

Rule order (first match wins); every verdict carries its evidence:
  R1 ability-form ("can/could you ...") + action/artifact -> request
  R2 interrogative form, no fleet-directed action -> question
  R3 imperative lead verb -> directive
  R4 hedge + concrete artifact noun -> request (proposed request;
     the 2026-11-01 miss class: "DoE likely it's own AppID && Repo
     etc" was read as speculation and verified instead of built)
  R5 action verb + artifact noun anywhere -> request
  R6 hedge/conditional, no artifact and no action -> speculation
  R7 default -> aside
Bias: asymmetric cost — a request missed as speculation is the
failure class, so R4/R5 fire before R6.
"""
import re

HEDGES = {"likely", "probably", "maybe", "perhaps", "should", "would",
          "could", "might", "possibly", "presumably", "imo"}
ARTIFACTS = {"appid", "repo", "repository", "pr", "prs", "build",
             "lane", "chat", "page", "workflow", "account", "app",
             "dashboard", "issue", "branch", "script", "connector",
             "model", "classifier", "feature", "release", "deploy"}
ACTION_VERBS = {"build", "add", "send", "create", "run", "land",
                "merge", "file", "check", "make", "set", "wire",
                "register", "start", "launch", "fix", "update",
                "write", "open", "close", "ship", "deploy", "route",
                "provision", "harvest", "steward", "follow"}
IMPERATIVE_LEADS = ACTION_VERBS | {"use", "take", "give", "show",
                                   "get", "put", "keep", "record"}
QUESTION_LEADS = {"how", "what", "why", "when", "where", "who",
                  "which", "is", "are", "does", "do", "did", "was",
                  "were", "has", "have"}
WORD = re.compile(r"[a-z]+(?:'[a-z]+)?")


def classify(text: str) -> dict:
    words = WORD.findall(text.lower())
    wset = set(words)
    hedges = sorted(wset & HEDGES)
    artifacts = sorted(wset & ARTIFACTS)
    actions = sorted(wset & ACTION_VERBS)
    ev = {"hedges": hedges, "artifacts": artifacts, "actions": actions}
    first = words[0] if words else ""
    # R1: ability-form request ("can you check ...?")
    if first in ("can", "could") and (actions or artifacts):
        return {"intent": "request", "rule": "R1-ability-form", **ev}
    # R2: interrogative, no fleet-directed action
    is_question = text.strip().endswith("?") or first in QUESTION_LEADS
    if is_question and not (first in IMPERATIVE_LEADS):
        if not (actions and artifacts):
            return {"intent": "question", "rule": "R2-interrogative", **ev}
    # R3: imperative lead
    if first in IMPERATIVE_LEADS:
        return {"intent": "directive", "rule": "R3-imperative", **ev}
    # R4: hedge + artifact -> proposed request (the miss class)
    if hedges and artifacts:
        return {"intent": "request", "rule": "R4-hedge+artifact", **ev}
    # R5: action + artifact anywhere
    if actions and artifacts:
        return {"intent": "request", "rule": "R5-action+artifact", **ev}
    # R6: hedge/conditional only -> speculation
    if hedges:
        return {"intent": "speculation", "rule": "R6-hedge-only", **ev}
    # R7: default
    return {"intent": "aside", "rule": "R7-default", **ev}


if __name__ == "__main__":
    import json
    import sys
    for line in sys.stdin:
        line = line.strip()
        if line:
            print(json.dumps({"text": line, **classify(line)}))
