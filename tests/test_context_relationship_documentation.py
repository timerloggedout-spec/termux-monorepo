import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def read(relative_path):
    return (ROOT / relative_path).read_text()


@pytest.mark.parametrize(
    ("page", "target"),
    [
        ("docs/icm/routing.md", "CLAUDE.md"),
        ("docs/icm/objects/governance/CONTEXT.hum.md", "CLAUDE.md"),
        ("docs/icm/objects/governance/CONTEXT.md", "CLAUDE.md"),
        ("docs/icm/maintenance/04_promote/CONTEXT.hum.md", "CLAUDE.md"),
        ("docs/icm/maintenance/04_promote/CONTEXT.md", "CLAUDE.md"),
        ("docs/icm/processes/change-and-validate.md", "CLAUDE.md"),
        ("docs/icm/_meta/method-coverage.md", "docs/icm/CLAUDE.md"),
    ],
)
def test_icm_guidance_links_resolve_to_the_intended_entrypoint(page, target):
    content = read(page)
    links = re.findall(r"\]\(([^\s)]+)\)", content)
    paths = {(ROOT / page).parent / link.split("#", 1)[0] for link in links}
    expected = ROOT / target
    assert expected.is_file()
    assert expected in {path.resolve() for path in paths}
    assert not any(path.name == "AGENTS.md" for path in paths)


def test_change_and_validate_links_to_the_execution_defaults_heading():
    page = Path("docs/icm/processes/change-and-validate.md")
    links = re.findall(r"\[repository execution defaults\]\(([^\s)]+)\)", read(page))
    assert len(links) == 1
    path, _, fragment = links[0].partition("#")
    target = ROOT / "CLAUDE.hum.md"
    assert (ROOT / page.parent / path).resolve() == target
    assert fragment == "execution-defaults"
    assert "## Execution defaults" in target.read_text().splitlines()


def test_claude_icm_catalog_routes_context_reconnaissance():
    catalog = read("docs/icm/CLAUDE.md")
    process = read("docs/icm/processes/context-relationship-reconnaissance.md")
    skill = read(".agents/skills/context-relationship-graph/SKILL.md")

    assert "context-relationship-reconnaissance.md" in catalog
    assert "verified relationship evidence" in process
    assert "candidate" in process
    assert "metadata-only" in skill


def test_icm_catalogs_register_the_new_object_and_process():
    assert "context-relationship-index.md" in read("docs/icm/objects/_index.md")
    assert "context-relationship-index.md" in read("docs/icm/effects/CONTEXT.md")
    assert "context-relationship-reconnaissance.md" in read("docs/icm/CLAUDE.md")
    assert "context-relationship-reconnaissance.md" in read("docs/icm/processes/CONTEXT.md")


def test_context_reconnaissance_artifacts_define_generated_and_candidate_boundaries():
    object_card = read("docs/icm/objects/knowledge/context-relationship-index.md")
    process_card = read("docs/icm/processes/context-relationship-reconnaissance.md")
    skill = read(".agents/skills/context-relationship-graph/SKILL.md")

    for content in (object_card, process_card, skill):
        assert "metadata-only" in content
        assert "candidate" in content
    assert "not hand-edited" in object_card
    assert "cross-referenced" in object_card
    assert "exact GitHub permalink" in process_card
    assert "history-page backfill" in process_card
    assert "Linear freshness" in object_card
    assert "Do not persist PR, issue" in skill
    assert "#discussion_r" in skill
    assert "file-review-timeline" in skill
