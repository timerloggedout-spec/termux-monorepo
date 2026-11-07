"""Pure, fail-closed gates for comment-triggered DeepSeek invocations.

Comment text is data. Only a newly-created comment by a trusted human repository
collaborator, beginning with an explicitly registered moniker, may invoke a
comment-driven DeepSeek route.
"""
from __future__ import annotations

import re
from typing import Any

TRUSTED_AUTHOR_ASSOCIATIONS = frozenset({"OWNER", "MEMBER", "COLLABORATOR"})
COMMENT_EVENT_NAMES = frozenset({"issue_comment", "pull_request_review_comment"})
_COMMAND_RE = re.compile(r"^@(deepseek-ci|deepseek|deepcore)(?=$|\s)", re.IGNORECASE)


def parse_comment_command(body: Any) -> dict[str, str] | None:
    """Parse an exact leading supported moniker; reject mentions embedded in prose."""
    if not isinstance(body, str):
        return None
    text = body.lstrip()
    match = _COMMAND_RE.match(text)
    if match is None:
        return None
    return {
        "alias": match.group(1).lower(),
        "request": text[match.end():].strip(),
    }


def is_trusted_comment_event(event: Any) -> bool:
    """Require a created comment from a human OWNER/MEMBER/COLLABORATOR."""
    if not isinstance(event, dict) or event.get("action") != "created":
        return False
    comment = event.get("comment")
    sender = event.get("sender")
    if not isinstance(comment, dict) or not isinstance(sender, dict):
        return False
    user = comment.get("user")
    if not isinstance(user, dict):
        return False
    association = str(comment.get("author_association") or "").upper()
    return (
        sender.get("type") == "User"
        and user.get("type") == "User"
        and association in TRUSTED_AUTHOR_ASSOCIATIONS
    )


def trusted_comment_request(event: Any, event_name: str) -> dict[str, str] | None:
    """Return parsed request only for real, supported, trusted comment events."""
    if event_name not in COMMENT_EVENT_NAMES or not is_trusted_comment_event(event):
        return None
    comment = event.get("comment") or {}
    return parse_comment_command(comment.get("body"))


def should_process_event(event: Any, event_name: str) -> bool:
    """Preflight before credentials/session setup; manual payloads cannot spoof comments."""
    if not isinstance(event, dict):
        return False
    if event_name in COMMENT_EVENT_NAMES:
        return trusted_comment_request(event, event_name) is not None
    if event.get("comment"):
        return False
    return True
