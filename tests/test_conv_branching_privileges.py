import os
import sys
import json
from pathlib import Path
import pytest

sys.path.insert(0, os.path.abspath("cli-synthegration"))
import conv_branching as cb

def test_conv_branching_input_validation(tmp_path):
    repo_dir = tmp_path / "conv_repo"
    repo = cb.ConversationRepo(repo_path=repo_dir)

    invalid_inputs = [
        "../traversal",
        "/absolute/path",
        "branch;injection",
        "branch name",
        "branch*!$",
        ""
    ]

    for invalid in invalid_inputs:
        with pytest.raises(ValueError, match="Invalid from_branch"):
            repo.link_knowledge(invalid, "branch2", "reference")

        with pytest.raises(ValueError, match="Invalid to_branch"):
            repo.link_knowledge("branch1", invalid, "reference")

        with pytest.raises(ValueError, match="Invalid link_type"):
            repo.link_knowledge("branch1", "branch2", invalid)


def test_conv_branching_symlink_safety(tmp_path):
    # 1. Test symlink repo directory
    real_repo = tmp_path / "real_repo"
    real_repo.mkdir(parents=True, exist_ok=True)

    symlink_repo = tmp_path / "symlink_repo"
    symlink_repo.symlink_to(real_repo, target_is_directory=True)

    repo_symlink = cb.ConversationRepo(repo_path=symlink_repo)
    with pytest.raises(ValueError, match="Symlink repository directory rejected"):
        repo_symlink.link_knowledge("branchA", "branchB", "reference")

    # 2. Test symlinked knowledge_links.jsonl file
    repo_dir = tmp_path / "conv_repo_file_symlink"
    repo_dir.mkdir(parents=True, exist_ok=True)

    target_file = tmp_path / "sensitive_target.txt"
    target_file.write_text("sensitive")
    if os.name != "nt":
        target_file.chmod(0o644)

    symlink_links = repo_dir / "knowledge_links.jsonl"
    symlink_links.symlink_to(target_file)

    repo = cb.ConversationRepo(repo_path=repo_dir)
    with pytest.raises(ValueError, match="Symlink knowledge links file rejected"):
        repo.link_knowledge("branchA", "branchB", "reference")

    if os.name != "nt":
        assert (target_file.stat().st_mode & 0o777) == 0o644


def test_conv_branching_privileges_and_link_creation(tmp_path):
    repo_dir = tmp_path / "conv_repo_valid"
    repo = cb.ConversationRepo(repo_path=repo_dir)

    link = repo.link_knowledge("branch1", "branch2", "reference-back")
    assert link["from"] == "branch1"
    assert link["to"] == "branch2"
    assert link["type"] == "reference-back"

    links_file = repo_dir / "knowledge_links.jsonl"
    assert links_file.exists()

    if os.name != "nt":
        assert (repo_dir.stat().st_mode & 0o777) == 0o700
        assert (links_file.stat().st_mode & 0o777) == 0o600

    content = links_file.read_text()
    assert "branch1" in content
    assert "branch2" in content
