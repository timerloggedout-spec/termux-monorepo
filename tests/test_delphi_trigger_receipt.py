import hashlib
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "delphi_trigger_receipt", ROOT / "scripts/proposals/delphi_trigger_receipt.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_existing_non_delphi_proposal_is_explicitly_not_triggered():
    entries = MODULE.registry_entries()
    receipt = MODULE.build_receipt("aws-free-tier-strands-delphi-oracle", "abc123", entries)
    assert receipt["status"] == "not_triggered"
    assert receipt["reason"] == "proposal_not_marked_for_delphi_participation"
    assert receipt["source_sha"] == "abc123"
    assert receipt["manifest_sha256"] == hashlib.sha256(
        (ROOT / "docs/proposals/active/aws-free-tier-strands-delphi-oracle/MANIFEST.md").read_bytes()
    ).hexdigest()


@pytest.mark.parametrize("proposal_id,title,marker,expected", [
    ("delphic-anonymity-method-participation", "Independent contributor participation", "", "triggered"),
    ("independent-a", "Independent proposal A", "delphi_trigger: true", "triggered"),
    ("ordinary-proposal", "Ordinary proposal", "", "not_triggered"),
])
def test_independent_proposal_identity_is_not_aliased(tmp_path, monkeypatch, proposal_id, title, marker, expected):
    # Keep this pure and isolated: synthesize each proposal independently.
    manifest_dir = tmp_path / "active" / proposal_id
    manifest_dir.mkdir(parents=True)
    manifest = manifest_dir / "MANIFEST.md"
    manifest.write_text(f"---\nid: {proposal_id}\n{marker}\n---\n", encoding="utf-8")
    monkeypatch.setattr(MODULE, "PROPOSALS_ROOT", tmp_path)
    entry = {"id": proposal_id, "title": title, "status": "in_review", "path": f"active/{proposal_id}/"}
    receipt = MODULE.build_receipt(proposal_id, "candidate-sha", {proposal_id: entry})
    assert receipt["status"] == expected
    assert receipt["proposal_id"] == proposal_id
    assert receipt["source_sha"] == "candidate-sha"


def test_unknown_id_never_substitutes_another_proposal():
    receipt = MODULE.build_receipt("unknown-proposal", "sha", MODULE.registry_entries())
    assert receipt["status"] == "not_triggered"
    assert receipt["reason"] == "proposal_id_not_registered"


def test_unsafe_manifest_path_is_rejected():
    with pytest.raises(ValueError, match="unsafe proposal path"):
        MODULE.build_receipt("unsafe", "sha", {"unsafe": {"id": "unsafe", "path": "../secret/"}})
