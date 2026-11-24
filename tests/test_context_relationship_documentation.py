from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(relative_path):
    return (ROOT / relative_path).read_text()


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
