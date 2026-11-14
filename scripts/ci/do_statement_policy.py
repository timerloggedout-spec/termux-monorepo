"""Pure DO-statement classification helpers for the review-only candidate."""
from __future__ import annotations
import re

ACTION_VERBS = {
    "accept", "add", "align", "apply", "audit", "build", "bump", "check",
    "close", "compare", "create", "define", "deploy", "document", "enforce",
    "expand", "fix", "gate", "include", "inspect", "keep", "measure",
    "migrate", "move", "open", "preserve", "guard", "publish", "record",
    "reconcile", "refresh", "refine", "register", "remove", "rename",
    "repair", "replace", "require", "restore", "route", "run", "set",
    "snapshot", "split", "sync", "test", "update", "use", "validate",
    "verify", "wire", "collect", "generate", "regenerate", "rebuild",
}
_EXPLICIT_DO = re.compile(r"^\s*DO\s*:\s*\S", re.IGNORECASE)
_PROHIBITION = re.compile(
    r"^\s*(?:(?:[-*]\s*)|(?:#+\s*))?(?:do not|don't|never|no\b|not\b|avoid\b)",
    re.IGNORECASE,
)
_HEDGED_FIRST = re.compile(
    r"^\s*(?:(?:[-*]\s*)|(?:#+\s*))?"
    r"(?:we should\b|we might\b|maybe we\b|perhaps we\b|"
    r"it might be (?:useful|good|better) to\b|"
    r"it would be (?:good|better|useful) to\b|"
    r"we could consider\b)",
    re.IGNORECASE,
)

def _plain_line(value: str) -> str:
    return re.sub(r"^\s*(?:(?:[-*+]\s+)|(?:#+\s+)|(?:\d+[.)]\s+))", "", value).strip()

def classify_instruction(value: str) -> str:
    line = _plain_line(value)
    if not line:
        return "empty"
    if _EXPLICIT_DO.match(line):
        return "explicit_do"
    if _PROHIBITION.match(line):
        return "constraint"
    if _HEDGED_FIRST.match(line):
        return "hedged"
    first = re.match(r"[A-Za-z]+", line)
    if first and first.group(0).lower() in ACTION_VERBS:
        return "natural_imperative"
    return "descriptive"

def is_hedged_instruction(value: str) -> bool:
    return classify_instruction(value) == "hedged"

def subject_action_verb(subject: str) -> str:
    tail = subject.rsplit(": ", 1)[-1].strip()
    tail = re.sub(r"^DO\s*:\s*", "", tail, flags=re.IGNORECASE)
    match = re.match(r"([A-Za-z]+)", tail)
    return match.group(1).lower() if match else ""
