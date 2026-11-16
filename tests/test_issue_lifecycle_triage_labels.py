"""Offline tests for the deterministic issue-lifecycle triage pass.

Pins the G1 fix contract (docs/ops/ISSUE-LIFECYCLE.md): the pass labels
only unlabelled issues, only from title-prefix rules, only with labels
that already exist in the repo taxonomy, and never touches a labelled
issue.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "issue_lifecycle"))

import io
import urllib.error

import pytest

import triage_labels
from triage_labels import KNOWN_LABELS, propose_labels  # noqa: E402


def test_proposal_investigate_gets_proposal_and_research():
    title = "Proposal: investigate TanStack AI 1.0 (stable provider adapters)"
    assert propose_labels(title, []) == ["proposal", "research"]


def test_plain_proposal_gets_proposal_only():
    assert propose_labels("Proposal: DOE pilot 1 - context routing", []) == ["proposal"]
    assert propose_labels("[proposal] mistral.workflows: dispatch overlay", []) == ["proposal"]


def test_target_brief_gets_target_label():
    assert propose_labels("[target] wolframalpha: api-extraction", []) == ["target-brief"]


def test_delphi_rfp_gets_delphi_label():
    assert propose_labels("[delphi:rfp] turso.free", []) == ["delphi:rfp"]


def test_bug_prefix_gets_bug():
    assert propose_labels("bug: gate fails on empty diff", []) == ["bug"]
    assert propose_labels("[bug] crash on startup", []) == ["bug"]


def test_labelled_issue_is_never_touched():
    assert propose_labels("Proposal: investigate X", ["proposal"]) == []
    assert propose_labels("[target] y: api-extraction", ["target-brief"]) == []


def test_unmatched_title_gets_nothing():
    assert propose_labels("BIUDL: Build the evidence-driven cockpit", []) == []
    assert propose_labels("[mesh] Integration mesh matrix - standing thread", []) == []
    assert propose_labels("", []) == []
    assert propose_labels(None, []) == []


def test_request_surfaces_http_error_and_exits(monkeypatch):
    """Regression (2026-10-28): the first version let a GitHub 403 kill
    the pass with no reason printed while the workflow step still
    reported success. _request must name the status and exit non-zero."""

    def fake_urlopen(req, timeout=0):
        raise urllib.error.HTTPError(
            req.full_url, 403, "Forbidden", {}, io.BytesIO(b"resource not accessible")
        )

    monkeypatch.setattr(triage_labels.urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(SystemExit) as excinfo:
        triage_labels._request("GET", "/issues?state=open", "token", "o/r")
    assert excinfo.value.code == 1


def test_request_sets_user_agent(monkeypatch):
    seen = {}

    class Resp:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return b"[]"

    def fake_urlopen(req, timeout=0):
        seen["ua"] = req.get_header("User-agent")
        return Resp()

    monkeypatch.setattr(triage_labels.urllib.request, "urlopen", fake_urlopen)
    assert triage_labels._request("GET", "/issues?state=open", "token", "o/r") == []
    assert seen["ua"] == triage_labels.USER_AGENT


def test_request_retries_rate_limit_then_succeeds(monkeypatch):
    """The shared Actions installation token is rate-limited in hot
    hours (proven live 2026-10-28); a rate-limit 403 must be retried,
    not fatal."""
    calls = {"n": 0}

    class Resp:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return b"[]"

    def fake_urlopen(req, timeout=0):
        calls["n"] += 1
        if calls["n"] == 1:
            raise urllib.error.HTTPError(
                req.full_url, 403, "Forbidden", {},
                io.BytesIO(b"API rate limit exceeded for installation"),
            )
        return Resp()

    monkeypatch.setattr(triage_labels.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(triage_labels.time, "sleep", lambda s: None)
    assert triage_labels._request("GET", "/issues?state=open", "token", "o/r") == []
    assert calls["n"] == 2


def test_mechanical_title_classes():
    """Rules added 2026-10-28 so the weekly workflow, not a human,
    clears the mechanical share of the unlabelled backlog."""
    cases = {
        "[Actions Incident] PR production ledger: failure": ["bug", "ci"],
        "[DPH-100] GitHub Projects synchronization": ["enhancement", "automation"],
        "deepagent task: verify live worker readiness": ["agent"],
        "fix(governance): register existing active proposal directories": ["bug"],
        "fix(workflows): restore CodeRabbit command-library approval trigger": ["bug"],
        "ops: expand contributor monikers and role registry across agent/provider lanes": ["ops"],
        "feat: uncertainty-aware routing, foresight and decision-evidence layer": ["enhancement"],
    }
    for title, want in cases.items():
        assert propose_labels(title, []) == want, title


def test_proposed_labels_always_exist_in_taxonomy():
    titles = [
        "Proposal: investigate A",
        "Proposal: build B",
        "[target] c: cli-adapter",
        "[delphi:rfp] d.free",
        "bug: e",
    ]
    for title in titles:
        for label in propose_labels(title, []):
            assert label in KNOWN_LABELS
