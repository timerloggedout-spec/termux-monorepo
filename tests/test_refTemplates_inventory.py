from scripts.ci import refTemplates_inventory as inventory


def test_tier_c_pattern_child_requires_readme_and_source(tmp_path, monkeypatch):
    monkeypatch.setattr(inventory, "ROOT", tmp_path)
    slot = tmp_path / "13_Third_Party_Refs"
    child = slot / "spaceship-ide"
    child.mkdir(parents=True)
    (child / "README.md").write_text("# Spaceship IDE\n", encoding="utf-8")
    (child / "SOURCE.txt").write_text("Preferred SOURCE: https://example.test/repo\n", encoding="utf-8")

    entry = inventory.inventory_entry(slot)

    assert entry["pattern_children"] == [
        {
            "name": "spaceship-ide",
            "has_source": True,
            "has_readme": True,
            "source_preview": "Preferred SOURCE: https://example.test/repo",
        }
    ]
    assert inventory.validate([entry]) == []


def test_tier_c_pattern_child_reports_each_missing_metadata_file(tmp_path, monkeypatch):
    monkeypatch.setattr(inventory, "ROOT", tmp_path)
    slot = tmp_path / "13_Third_Party_Refs"
    (slot / "spaceship-ide").mkdir(parents=True)

    entry = inventory.inventory_entry(slot)

    assert inventory.validate([entry]) == [
        "13_Third_Party_Refs/spaceship-ide: missing SOURCE.txt",
        "13_Third_Party_Refs/spaceship-ide: missing README.md",
    ]


def test_tier_a_research_child_contract_remains_intact(tmp_path, monkeypatch):
    monkeypatch.setattr(inventory, "ROOT", tmp_path)
    slot = tmp_path / "15_Research_Repo_Templates"
    child = slot / "sample-research-template"
    child.mkdir(parents=True)
    (child / "README.md").write_text("# Sample\n", encoding="utf-8")
    (child / "SOURCE.txt").write_text("Preferred SOURCE: https://example.test/repo\n", encoding="utf-8")

    entry = inventory.inventory_entry(slot)

    assert entry["research_children"][0]["has_source"] is True
    assert entry["research_children"][0]["has_readme"] is True
    assert inventory.validate([entry]) == []
