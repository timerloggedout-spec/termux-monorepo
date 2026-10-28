"""Classifier tests for the comment-quality sweep.

The sweep may delete only two exact classes; every fixture below pins
one side of that line. Productive look-alikes (a completed triage, a
Blocks-authored comment that is not the pitch, a ledger event) must
never classify as deletable.
"""
import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "comment_quality_sweep", ROOT / "scripts" / "comment_quality_sweep.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def c(author, body):
    return {"user": {"login": author}, "body": body}


def test_blocks_pitch_is_vendor_promo():
    body = "Mention Blocks like a regular teammate with your question or request:\n\n@blocks ..."
    assert mod.classify(c("blocksorg[bot]", body)) == "vendor-promo"


def test_blocks_author_without_pitch_is_not_deletable():
    assert mod.classify(c("blocksorg[bot]", "Investigated: the query plan is in the linked run.")) \
        == "substantive-other"


def test_pitch_text_from_another_author_is_not_deletable():
    body = "Mention Blocks like a regular teammate — quoting the spam drop for the record."
    assert mod.classify(c("timerloggedout-spec", body)) == "substantive-other"


def test_failed_triage_stub_is_automation_failure():
    body = ("<!-- openrouter-triage -->\n### OpenRouter triage\n\n"
            "⚠️ openrouter invocation incomplete. HTTP 429; curl_exit=0; bytes=642.")
    assert mod.classify(c("github-actions[bot]", body)) == "automation-failure"


def test_completed_triage_is_productive():
    body = ("<!-- openrouter-triage -->\n### OpenRouter triage\n\n"
            "**Classification:** Feature\n**Labels:** `enhancement`, `delphi`")
    assert mod.classify(c("github-actions[bot]", body)) == "substantive-other"


def test_ledger_event_and_signed_append_are_productive():
    assert mod.classify(c("github-actions[bot]", "<!-- delphi-outcomes v1 -->\nstate")) == "ledger-event"
    assert mod.classify(c("timerloggedout-spec", "[MUSEai]@{role:{delphi-lane}} — correction")) == "signed-append"


def test_unknown_comment_is_never_deletable():
    assert mod.classify(c("some-human", "Evidence: run 123, see artifact.")) == "substantive-other"
    assert mod.DELETABLE == ("vendor-promo", "automation-failure")
