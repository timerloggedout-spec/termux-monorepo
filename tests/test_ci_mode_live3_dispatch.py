"""Tests for the ci_mode live-3 dispatch opt-in (ruling (i-a)).

The amendment is marker-gated: only a PR issue_comment carrying
the live-3 stamp header is treated as a designed dispatch (comment
body = composed prompt). Everything else must return None so the
surface's behavior is unchanged. Dispatch administration is also
author-gated: only repository-trusted authors (OWNER / MEMBER /
COLLABORATOR) may trigger one — the marker alone must never let
an arbitrary commenter drive the bot's prompt.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]


def _load():
    # Stub the heavy backend modules ci_mode imports at top level.
    for name in ("backends", "backends.deepseek", "core",
                 "core.session_manager"):
        if name not in sys.modules:
            m = ModuleType(name)
            sys.modules[name] = m
    sys.modules["backends.deepseek"].DeepSeekBackend = object
    sys.modules["backends.deepseek"].WASM_SOLVER = None
    sys.modules["core.session_manager"].SessionManager = object
    spec = importlib.util.spec_from_file_location(
        "ci_mode", ROOT / "deepcli/ci_mode.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CI = _load()

HEADER = ("[MUSEai]@{role:{doe-mgr-phrases-jit}} — "
          "live-3-phrases-deepseek dispatch #2 · cell `suffix-vowels` "
          "(stage 1, fixed-anchor) · route deepseek-ci comment "
          "surface (ALT, ruling (a)) · prompt sha256 `3049363b2ea4` "
          "· instance `9dfabcd6f25f`")
PROMPT = "Review this pull request.\n\nPR #2436: the diff."


def event(body, *, pr_issue=True, action="created", assoc="OWNER"):
    return {"action": action,
            "comment": {"body": body,
                        "author_association": assoc},
            "issue": {"number": 2436,
                      "pull_request": {"url": "x"} if pr_issue
                      else None}}


def test_dispatch_parsed_and_envelope_stripped():
    d = CI._live3_dispatch(event(HEADER + "\n\n" + PROMPT))
    assert d is not None
    assert d["pr"] == 2436
    assert d["prompt"] == PROMPT
    assert d["stamp"] == {"dispatch_no": 2, "cell": "suffix-vowels",
                          "prompt_sha256_12": "3049363b2ea4",
                          "instance_12": "9dfabcd6f25f"}


def test_unmarked_comment_is_not_a_dispatch():
    assert CI._live3_dispatch(event("please review @deepseek")) \
        is None


def test_marker_on_plain_issue_is_not_a_dispatch():
    assert CI._live3_dispatch(
        event(HEADER + "\n\n" + PROMPT, pr_issue=False)) is None


def test_non_created_action_is_not_a_dispatch():
    assert CI._live3_dispatch(
        event(HEADER + "\n\n" + PROMPT, action="edited")) is None


def test_pull_request_event_is_not_a_dispatch():
    ev = {"action": "opened",
          "pull_request": {"number": 2436, "body": HEADER}}
    assert CI._live3_dispatch(ev) is None


def test_untrusted_author_is_not_a_dispatch():
    for assoc in ("NONE", "FIRST_TIME_CONTRIBUTOR",
                  "FIRST_TIMER", None):
        assert CI._live3_dispatch(
            event(HEADER + "\n\n" + PROMPT, assoc=assoc)) is None
    for assoc in ("OWNER", "MEMBER", "COLLABORATOR"):
        assert CI._live3_dispatch(
            event(HEADER + "\n\n" + PROMPT, assoc=assoc)) is not None
