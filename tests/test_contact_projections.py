"""Regression coverage for deterministic Linguist contact-document projections."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "cedrlang" / "render_contact_projections.py"
SPEC = importlib.util.spec_from_file_location("contact_projections", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
contact_projections = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = contact_projections
SPEC.loader.exec_module(contact_projections)


def test_display_projection_transforms_prose_but_preserves_markdown_destinations_and_fences() -> None:
    source = """# Agent workflow\n\nRead [agent path](docs/icm/AGENTS.md).\n\n```bash\nagent path\n```\n"""

    rendered = contact_projections.render(
        source,
        Path("README.hum.md"),
        "display-l33t-v1",
    )

    assert "# 4g3n7 w0rkfl0w" in rendered
    assert "[4g3n7 p47h](docs/icm/AGENTS.md)" in rendered
    assert "```bash\nagent path\n```" in rendered
    assert "source=README.hum.md" in rendered


def test_machine_projection_obfuscates_prose_path_name_and_value_terms() -> None:
    source = "Agent path name value workflow.\n"

    rendered = contact_projections.render(
        source,
        Path("AGENTS.hum.md"),
        "machine-grimoire-seed-v1",
    )

    assert "§01§ §14§ §12§ §1e§ §20§." in rendered
    assert "§a1§ §a3§ §a2§ §a4§ §a7§." in contact_projections.render(
        "Files paths names values workflows.\n",
        Path("AGENTS.hum.md"),
        "machine-grimoire-seed-v1",
    )
    assert "source=AGENTS.hum.md" in rendered


def test_repository_contact_tree_has_complete_current_projections() -> None:
    projections = contact_projections.discover(ROOT)

    assert len(projections) == 24
    for projection in projections:
        expected = contact_projections.render(
            (ROOT / projection.source).read_text(encoding="utf-8"),
            projection.source,
            projection.mode,
        )
        assert (ROOT / projection.target).read_text(encoding="utf-8") == expected


def test_write_then_check_detects_stale_projection(tmp_path: Path) -> None:
    (tmp_path / "README.hum.md").write_text("Agent workflow.\n", encoding="utf-8")
    (tmp_path / "AGENTS.hum.md").write_text("Agent path.\n", encoding="utf-8")

    assert contact_projections.write_or_check(tmp_path, check=False) == 0
    assert contact_projections.write_or_check(tmp_path, check=True) == 0

    (tmp_path / "AGENTS.md").write_text("stale\n", encoding="utf-8")
    assert contact_projections.write_or_check(tmp_path, check=True) == 1
