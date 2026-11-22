import json
from pathlib import Path

import pytest

from scripts.ci import refTemplates_inventory as inventory


@pytest.mark.parametrize(
    "slot_name",
    ["15_Research_Repo_Templates", "19_Provider_Inference_Catalogs"],
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

    assert entry["research_children"] == entry["metadata_children"] == [
        {
            "name": "jogyo",
            "has_source": True,
            "has_readme": True,
            "source_preview": "https://example.test",
        }
    ]
    assert inventory.validate([entry]) == []


def test_whitespace_only_source_file_has_empty_preview(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    ref = root / "refTemplates"
    slot = ref / "19_Provider_Inference_Catalogs"
    child = slot / "vultr-model-catalog-python"
    child.mkdir(parents=True)
    (child / "README.md").write_text("reference\n", encoding="utf-8")
    (child / "SOURCE.txt").write_text("  \n\t\n", encoding="utf-8")
    monkeypatch.setattr(inventory, "ROOT", root)
    monkeypatch.setattr(inventory, "REF", ref)

    entry = inventory.inventory_entry(slot)

    assert entry["metadata_children"][0]["source_preview"] is None
    assert inventory.validate([entry]) == []


def test_provider_catalog_doe_registry_compares_native_variants_and_pins_references():
    root = Path(__file__).resolve().parents[1]
    registry_path = (
        root / "refTemplates" / "19_Provider_Inference_Catalogs" / "DOE-REGISTRY.json"
    )
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    experiment = registry["experiment"]

    assert experiment["id"] == "DOE-VULTR-CATALOG-001"
    assert experiment["version"] == "2.0.0"
    assert experiment["status"] == "planned"
    assert {variant["catalogue"] for variant in experiment["variants"]} == {
        "Incumbent", "VultrInspired"
    }
    assert {source["revision"] for source in experiment["source_references"]} == {
        "4a414ab26e1f596cb98b3974a7d12182bf62dab3",
        "6e55057cb718213937c4c118271f5a2ca1779d0d",
    }
    assert experiment["execution_policy"]["network_mode"] == "disabled"
    assert experiment["execution_policy"]["credentials"] == "none"
    assert experiment["execution_policy"]["inference_mode"] == "disabled"
    assert experiment["execution_policy"]["result_artifacts"] == []
