"""Offline tests for the D0 package: fetch_evidence + the agent tool loop.

A fake transport stands in for the GitHub API, so the suite is fully
deterministic: no network, no credentials. The demo (demo.py) is the
live run; these tests pin the contract it relies on.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "apps" / "weekend-challenge-delphi-oracle"
sys.path.insert(0, str(APP))

from agent import run_agent  # noqa: E402
from fetch_evidence import CountingTransport, fetch_evidence  # noqa: E402

NOW = datetime(2026, 10, 27, tzinfo=timezone.utc)

PR = {"state": "closed", "merged_at": "2026-10-27T06:56:07Z",
      "head": {"sha": "81a0d77be3ae"}}
CHECKS = {"check_runs": [
    {"name": "hygiene + portability gate", "conclusion": "success"},
    {"name": "agentic termux smoke", "conclusion": "success"},
]}


def fake_transport(method, path):
    assert method == "GET"
    if path.endswith("/pulls/1620"):
        return PR
    if "check-runs" in path:
        return CHECKS
    if "contents/" in path:
        return {"sha": "abc123", "size": 5691}
    raise AssertionError(f"unexpected path: {path}")


def test_fetch_evidence_stamps_provenance_and_freshness():
    ev = fetch_evidence({"kind": "pull_request", "ref": 1620},
                        transport=fake_transport, now=NOW)
    assert ev["material"] is True
    assert ev["assembled_at"] == "2026-10-27T00:00:00Z"
    assert ev["fresh_until"] == "2026-10-27T00:15:00Z"
    claims = {it["claim"]: it["value"] for it in ev["items"]}
    assert claims["pr.merged"] is True
    assert claims["check:hygiene + portability gate"] == "success"
    assert all(it["provenance"]["source"] == "github-api" for it in ev["items"])
    assert all(it["sha256"] for it in ev["items"])


def test_fetch_evidence_is_read_only():
    counting = CountingTransport(fake_transport)
    try:
        counting("POST", "/repos/x")
    except ValueError:
        pass
    else:
        raise AssertionError("non-GET must be refused")
    assert counting.calls == 0


def test_agent_abstains_on_asserted_evidence_only():
    receipt = run_agent({"id": "t1", "action": "inspect", "asserted": True},
                        transport=fake_transport, now=NOW)
    assert receipt["decision_on_asserted_evidence"] == "ABSTAIN"
    assert receipt["decision_final"] == "ABSTAIN"
    assert receipt["tool_calls"]["fetch_evidence"] == 0
    assert receipt["external_calls"] == 0


def test_agent_allows_on_fetched_material_evidence():
    receipt = run_agent(
        {"id": "t2", "action": "inspect", "asserted": True,
         "artifact": {"kind": "pull_request", "ref": 1620}},
        transport=fake_transport, now=NOW)
    assert receipt["decision_on_asserted_evidence"] == "ABSTAIN"
    assert receipt["decision_final"] == "ALLOW_RECOMMENDATION"
    assert receipt["evidence_set"]["material"] is True
    assert receipt["external_calls"] == 2  # PR + its check runs, both GET
    assert receipt["deployment"] is False


def test_agent_escalates_consequential_even_with_evidence():
    receipt = run_agent(
        {"id": "t3", "action": "credential_mutation",
         "risk_tier": "consequential", "asserted": True,
         "artifact": {"kind": "file", "ref": ".github/workflows/delphi-gate.yml"}},
        transport=fake_transport, now=NOW)
    assert receipt["decision_final"] == "ESCALATE"
    assert receipt["evidence_set"]["material"] is True
