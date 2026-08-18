from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(relative_path):
    return (ROOT / relative_path).read_text()


def test_agents_routes_nontrivial_work_to_context_reconnaissance_and_skill():
    content = read("AGENTS.md")

    assert "context-relationship-reconnaissance.md" in content
    assert ".agents/skills/context-relationship-graph/SKILL.md" in content
    assert "verified evidence" in content
    assert "scored **candidates**" in content


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
    assert "Do not persist PR, issue, review, or comment bodies" in skill
