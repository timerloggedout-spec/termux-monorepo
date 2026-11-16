import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "harvest_deepwiki_structure",
    Path(__file__).resolve().parents[1] / "scripts" / "agentic" / "harvest_deepwiki_structure.py",
)
mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mod)

STRUCTURE = """Available pages for timerloggedout-spec/termux-monorepo:

- 1 Repository Overview
  - 1.1 Getting Started & Navigation
  - 1.2 Interpretable Context Methodology (ICM)
- 11 Glossary
"""


def test_parse_structure():
    rows = mod.parse_structure(STRUCTURE)
    assert rows == [
        ("1", "Repository Overview", "topic"),
        ("1.1", "Getting Started & Navigation", "subpage"),
        ("1.2", "Interpretable Context Methodology (ICM)", "subpage"),
        ("11", "Glossary", "topic"),
    ]


def test_section_roundtrip_and_provenance():
    rows = mod.parse_structure(STRUCTURE)
    section = mod.build_section(
        "timerloggedout-spec/termux-monorepo", rows, "2026-11-01T23:37Z", "ICM maintenance run #10"
    )
    assert "source_surface: DeepWiki.com" in section
    assert "evidence_class: generated-external" in section
    assert "Counts: 2 topics, 2 subpages, 4 pages total." in section
    record = "# DeepWiki.com Import Record\n" + section
    assert mod.latest_section_rows(record) == rows


def test_latest_section_rows_none_without_harvest():
    assert mod.latest_section_rows("# DeepWiki.com Import Record\n") is None


def test_not_indexed_section_records_no_structure():
    section = mod.build_not_indexed_section(
        "timerloggedout-spec/termux-monorepo", "2026-11-01T23:37Z", "automated harvest"
    )
    assert "status: not_indexed" in section
    assert "| # | Topic |" not in section
