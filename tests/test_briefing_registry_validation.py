"""Briefing registry validation contracts."""

from scripts.briefing import validate_registry


def test_procurement_registry_accepts_technical_records_without_license_metadata():
    """The production procurement ledger carries technical evidence only."""
    rows = validate_registry.load_jsonl(validate_registry.DATA / "procurement.jsonl")
    assert rows
    assert all("license" not in record for _, record in rows)
    validate_registry.validate_procurement()



def test_migrated_procurement_values_keep_source_provenance():
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    path = root / "research" / "legal-licensing" / "PROCUREMENT-LICENSE-OBSERVATIONS.jsonl"
    rows = validate_registry.load_jsonl(path)
    assert rows
    for _, record in rows:
        assert record["source_record_path"] == "data/briefing/procurement.jsonl"
        assert record["source_record_commit"] == "874ade3df06e95c0afa0c0142ecd9e5ef3bc177e"
        assert record["source_record_blob_sha"] == "f084c6f0040e7d4ec4f295781b8f8ff257b42421"
        assert record["source_record_line"] > 0
