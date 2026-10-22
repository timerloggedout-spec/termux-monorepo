from pathlib import Path


def test_wingman_submodule_is_pinned_and_documented():
    root = Path(__file__).resolve().parents[1]
    gitmodules = (root / ".gitmodules").read_text(encoding="utf-8")
    assert 'path = refTemplates/smods/Wingman_fork' in gitmodules
    assert 'url = https://github.com/timerloggedout-spec/Wingman_fork.git' in gitmodules
    skill = (root / ".agents/skills/wingman-project-integration/SKILL.md").read_text(encoding="utf-8")
    assert 'a6d5cea2d48009b5555e138c8d6b8f620388fb1b' in skill
    assert 'RE-FETCH' in skill
    assert 'COMPARE' in skill


def test_adopted_skill_surfaces_are_loadable():
    root = Path(__file__).resolve().parents[1]
    for name in (
        "termux-mcp-project-steward",
        "context-relationship-graph",
        "wingman-project-integration",
    ):
        path = root / ".agents/skills" / name / "SKILL.md"
        assert path.is_file(), name
        assert path.read_text(encoding="utf-8").startswith("---\nname:")
