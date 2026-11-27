import json
from pathlib import Path
from scripts.ci.validate_historical_corpus_explorer_domain_atlas import validate_domain_atlas

ROOT = Path(__file__).resolve().parents[1]
ATLAS_PATH = ROOT / "apps/historical-corpus-explorer/data/domain-atlas.json"


def test_committed_domain_atlas_has_resolved_evidence_backed_relationships():
    atlas = json.loads(ATLAS_PATH.read_text(encoding="utf-8"))
    assert validate_domain_atlas(atlas) == []


def test_relationship_with_unknown_endpoint_is_rejected():
    atlas = json.loads(ATLAS_PATH.read_text(encoding="utf-8"))
    atlas["relationships"][0]["target"] = "missing-domain"
    assert any("target does not resolve" in error for error in validate_domain_atlas(atlas))


def test_verified_relationship_requires_evidence():
    atlas = json.loads(ATLAS_PATH.read_text(encoding="utf-8"))
    atlas["relationships"][0]["evidence"] = []
    assert any("verified relationships require evidence" in error for error in validate_domain_atlas(atlas))


def test_evidence_links_require_https():
    atlas = json.loads(ATLAS_PATH.read_text(encoding="utf-8"))
    atlas["domains"][0]["sources"][0]["url"] = "javascript:alert(1)"
    assert any("absolute HTTPS URL" in error for error in validate_domain_atlas(atlas))


def test_duplicate_domain_ids_are_rejected():
    atlas = json.loads(ATLAS_PATH.read_text(encoding="utf-8"))
    atlas["domains"].append(dict(atlas["domains"][0]))
    assert any("duplicates" in error for error in validate_domain_atlas(atlas))


def test_source_sha_must_be_immutable_full_revision():
    atlas = json.loads(ATLAS_PATH.read_text(encoding="utf-8"))
    atlas["source_sha"] = "master"
    assert any("full 40-character" in error for error in validate_domain_atlas(atlas))
