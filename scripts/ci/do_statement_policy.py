"""Pure, deterministic DO-statement authoring rules.

Natural imperatives and explicit DO markers are equivalent. Necessary
prohibitions remain valid constraints; narrowly defined hedging is rejected.
"""
from __future__ import annotations
import re

ACTION_VERBS = frozenset({
    "accept", "add", "align", "allow", "apply", "assert", "audit", "block", "bound",
    "build", "bump", "canonicalize", "centralize", "carry", "check", "close", "collect",
    "compare", "consolidate", "constrain", "correct", "cover", "create", "define", "deploy",
    "differentiate", "distinguish", "document", "emit", "enforce", "exclude", "exercise",
    "expand", "export", "extend", "fix", "gate", "generate", "guard", "include", "inspect",
    "keep", "lock", "measure", "migrate", "move", "normalize", "open", "pass", "preserve",
    "prevent", "propagate", "publish", "recognize", "record", "reconcile", "refresh", "refine",
    "register", "reject", "remove", "rename", "repair", "replace", "require", "restore", "retain",
    "route", "run", "set", "share", "skip", "snapshot", "specify", "split", "support", "sync",
    "test", "update", "use", "validate", "verify", "wire",
})
_EXPLICIT_DO = re.compile(r"^\s*DO\s*:\s*\S", re.IGNORECASE)
_PROHIBITION = re.compile(
    r"^\s*(?:(?:[-*+]\s+)|(?:#+\s+)|(?:\d+[.)]\s+))?"
    r"(?:do\s+not|don't|never|no\b|not\b|avoid\b)", re.IGNORECASE,
)
_HEDGED_FIRST = re.compile(
    r"^\s*(?:(?:[-*+]\s+)|(?:#+\s+)|(?:\d+[.)]\s+))?"
    r"(?:we\s+should\b|we\s+might\b|maybe\s+we\b|perhaps\s+we\b|"
    r"it\s+might\s+be\s+(?:useful|good|better)\s+to\b|"
    r"it\s+would\s+be\s+(?:good|better|useful)\s+to\b|"
    r"we\s+could\s+consider\b|it\s+may\s+be\s+worth\s+considering\b)",
    re.IGNORECASE,
)
_DECORATION = re.compile(r"^\s*(?:(?:[-*+]\s+)|(?:#+\s+)|(?:\d+[.)]\s+))")

def plain_line(value: str) -> str:
    return _DECORATION.sub("", value).strip()

def classify_instruction(value: str) -> str:
    """Return explicit_do, natural_imperative, constraint, hedged, descriptive, or empty."""
    line = plain_line(value)
    if not line:
        return "empty"
    if _EXPLICIT_DO.match(line):
        return "explicit_do"
    if _PROHIBITION.match(line):
        return "constraint"
    if _HEDGED_FIRST.match(line):
        return "hedged"
    first = re.match(r"([A-Za-z]+)", line)
    if first and first.group(1).lower() in ACTION_VERBS:
        return "natural_imperative"
    return "descriptive"

def is_hedged_instruction(value: str) -> bool:
    return classify_instruction(value) == "hedged"

def subject_action_verb(subject: str) -> str:
    """Extract the imperative after an optional conventional scope and DO marker."""
    tail = subject.rsplit(": ", 1)[-1].strip()
    tail = re.sub(r"^DO\s*:\s*", "", tail, flags=re.IGNORECASE)
    match = re.match(r"([A-Za-z]+)", tail)
    return match.group(1).lower() if match else ""

def is_imperative_subject(subject: str) -> bool:
    return subject_action_verb(subject) in ACTION_VERBS
