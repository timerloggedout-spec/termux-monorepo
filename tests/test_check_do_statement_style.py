import runpy
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "ci" / "check_do_statement_style.py"


def load_style_module(monkeypatch):
    for key in ("GITHUB_EVENT_NAME", "GITHUB_BASE_REF", "GITHUB_EVENT_PATH"):
        monkeypatch.delenv(key, raising=False)
    return runpy.run_path(str(SCRIPT))


def test_block_is_an_imperative_commit_verb(monkeypatch):
    module = load_style_module(monkeypatch)
    assert "block" in module["IMPERATIVE"]
    assert module["subject_verb"]("test(amd-academy): block unpromoted provider execution") == "block"


def test_commit_subject_scan_ignores_synthetic_merge_commits(monkeypatch):
    module = load_style_module(monkeypatch)
    calls = []

    def fake_run(args, **kwargs):
        calls.append(args)
        return SimpleNamespace(stdout="test(ci): add style regression coverage\n")

    monkeypatch.setattr(module["subprocess"], "run", fake_run)
    module["commit_subjects"]("origin/master", "HEAD")
    assert calls
    assert "--no-merges" in calls[0]


def test_commit_body_scan_ignores_synthetic_merge_commits(monkeypatch):
    module = load_style_module(monkeypatch)
    calls = []

    def fake_run(args, **kwargs):
        calls.append(args)
        return SimpleNamespace(stdout="")

    monkeypatch.setattr(module["subprocess"], "run", fake_run)
    module["commit_bodies"]("origin/master", "HEAD")
    assert calls
    assert "--no-merges" in calls[0]
