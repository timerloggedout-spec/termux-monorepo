"""Briefing registry validation contracts."""

from scripts.briefing import validate_registry


def test_procurement_registry_accepts_technical_records_without_license_metadata():
    """The production procurement ledger carries technical evidence only."""
    rows = validate_registry.load_jsonl(validate_registry.DATA / "procurement.jsonl")
    assert rows
    assert all("license" not in record for _, record in rows)
    validate_registry.validate_procurement()
