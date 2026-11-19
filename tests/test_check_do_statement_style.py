import runpy
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


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


def test_repo_action_verbs_are_recognized_as_imperative(monkeypatch):
    module = load_style_module(monkeypatch)
    verbs = {
        "allow", "assert", "block", "canonicalize", "centralize", "constrain",
        "cover", "correct", "carry", "distinguish", "emit", "exclude", "extend", "lock", "propagate", "reject", "share", "specify",
        "support", "pass", "prevent", "normalize", "recognize", "skip", "ignore",
    }
    assert verbs <= module["IMPERATIVE"]


def test_preserves_baseline_action_verbs(monkeypatch):
    # Master 069a774cd0ab06bc6ea6f8c51bd9e97ca3b895fd accepts these verbs.
    module = load_style_module(monkeypatch)
    assert {
        "account", "bind", "clarify", "export", "format", "guard", "implement",
        "initialize", "invoke", "isolate", "link", "parse", "pin", "sort",
    } <= module["IMPERATIVE"]


def run_push_check(tmp_path, subject, *, body="", instruction="Preserve checks.\n", script=SCRIPT):
    """Exercise the public CLI with a real, credential-free Git commit range."""
    def git(*args):
        return subprocess.run(
            ["git", *args], cwd=tmp_path, check=True, capture_output=True, text=True,
        ).stdout.strip()

    git("init", "--initial-branch=main")
    git("config", "user.name", "Style Regression")
    git("config", "user.email", "style-regression@example.invalid")
    git("config", "commit.gpgSign", "false")
    git("commit", "--allow-empty", "-m", "test: add baseline")
    before = git("rev-parse", "HEAD")
    path = tmp_path / "docs" / "ops" / "instructions.md"
    path.parent.mkdir(parents=True)
    path.write_text(instruction, encoding="utf-8")
    git("add", "docs")
    git("commit", "-m", subject, "-m", body)
    after = git("rev-parse", "HEAD")
    event = tmp_path / "push.json"
    event.write_text(json.dumps({"before": before, "after": after}), encoding="utf-8")
    env = os.environ.copy()
    env.update(GITHUB_EVENT_NAME="push", GITHUB_EVENT_PATH=str(event), GITHUB_BASE_REF="")
    return subprocess.run(
        [sys.executable, str(script)], cwd=tmp_path, env=env,
        capture_output=True, text=True, check=False,
    )


@pytest.mark.parametrize("subject", [
    "fix(ci): correct residual YAML scalar heuristics",
    "fix(ci): recognize explicit quoted mapping keys",
    "test(ci): add CLI regression coverage",
    "fix(ci): guard dispatch admission",
])
def test_real_push_accepts_imperative_subjects(tmp_path, subject):
    result = run_push_check(tmp_path, subject)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "DO-statement style: PASS" in result.stdout


@pytest.mark.parametrize("subject", [
    "fix(ci): corrected residual YAML scalar heuristics",
    "fix(ci): recognized explicit quoted mapping keys",
    "fix(ci): miscellaneous cleanup",
    "fix(ci): guarded dispatch admission",
])
def test_real_push_rejects_non_imperative_subjects(tmp_path, subject):
    result = run_push_check(tmp_path, subject)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "commit subject requires an imperative action verb" in result.stdout
    assert subject in result.stdout


@pytest.mark.parametrize("location", ["body", "instruction"])
def test_real_push_preserves_negative_first_rejection(tmp_path, location):
    kwargs = {location: "Do not bypass validation.\n"}
    result = run_push_check(tmp_path, "fix(ci): correct scalar boundaries", **kwargs)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "lead with the intended DO action" in result.stdout
    expected = "commit.body" if location == "body" else "docs/ops/instructions.md"
    assert expected in result.stdout
    assert "commit subject requires" not in result.stdout


def test_real_push_ignores_ambient_commit_signing(tmp_path, monkeypatch):
    config = tmp_path / "global.config"
    config.write_text(
        "[commit]\n gpgSign = true\n[gpg]\n program = /bin/false\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(config))
    repo = tmp_path / "repo"
    repo.mkdir()
    result = run_push_check(repo, "test(ci): add unsigned fixture coverage")
    assert result.returncode == 0, result.stdout + result.stderr
    assert config.read_text(encoding="utf-8").startswith("[commit]\n gpgSign = true")
