from scripts.ci import refTemplates_inventory as inventory

import pytest


@pytest.mark.parametrize(
    "slot_name",
    [
        "15_Research_Repo_Templates",
        "18_Vector_Databases",
        "19_Provider_Inference_Catalogs",
    ],
)
def test_metadata_reference_slots_require_source_and_readme(tmp_path, monkeypatch, slot_name):
    root = tmp_path / "repo"
    ref = root / "refTemplates"
    slot = ref / slot_name
    child = slot / "reference"
    child.mkdir(parents=True)
    (child / "README.md").write_text("reference\n", encoding="utf-8")
    monkeypatch.setattr(inventory, "ROOT", root)
    monkeypatch.setattr(inventory, "REF", ref)

    entry = inventory.inventory_entry(slot)

    assert inventory.validate([entry]) == [f"{slot_name}/reference: missing SOURCE.txt"]


def test_complete_provider_inference_reference_passes(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    ref = root / "refTemplates"
    slot = ref / "19_Provider_Inference_Catalogs"
    child = slot / "vultr-model-catalog-typescript"
    child.mkdir(parents=True)
    (child / "README.md").write_text("reference\n", encoding="utf-8")
    (child / "SOURCE.txt").write_text(
        "https://github.com/vultr/model-catalog-typescript\n", encoding="utf-8"
    )
    monkeypatch.setattr(inventory, "ROOT", root)
    monkeypatch.setattr(inventory, "REF", ref)

    entry = inventory.inventory_entry(slot)

    assert inventory.validate([entry]) == []


def test_legacy_research_children_field_remains_available(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    ref = root / "refTemplates"
    slot = ref / "15_Research_Repo_Templates"
    child = slot / "jogyo"
    child.mkdir(parents=True)
    (child / "README.md").write_text("reference\n", encoding="utf-8")
    (child / "SOURCE.txt").write_text("https://example.test\n", encoding="utf-8")
    monkeypatch.setattr(inventory, "ROOT", root)
    monkeypatch.setattr(inventory, "REF", ref)

    entry = inventory.inventory_entry(slot)

    assert entry["research_children"] == entry["metadata_children"]
    assert inventory.validate([entry]) == []
