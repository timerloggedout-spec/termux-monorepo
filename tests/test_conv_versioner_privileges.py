import os
import sys
import json
from pathlib import Path
import pytest

sys.path.insert(0, os.path.abspath("cli-synthegration"))
from conv_versioner import ConversationDAG, MessageRef


def test_conv_versioner_path_traversal_rejection(tmp_path):
    dag = ConversationDAG("session_123", "Test Title")
    dag.add_message({"id": "m1", "role": "user", "content": "hello world"})

    traversal_path = tmp_path / "foo" / ".." / "bar"

    with pytest.raises(ValueError, match="Path traversal rejected"):
        dag.commit(traversal_path)

    with pytest.raises(ValueError, match="Path traversal rejected"):
        ConversationDAG.load(traversal_path)


def test_conv_versioner_symlink_safety(tmp_path):
    dag = ConversationDAG("session_123", "Test Title")
    dag.add_message({"id": "m1", "role": "user", "content": "hello world"})

    # 1. Symlink repo_dir rejected
    target_repo = tmp_path / "real_repo"
    target_repo.mkdir(parents=True, exist_ok=True)
    symlink_repo = tmp_path / "symlink_repo"
    symlink_repo.symlink_to(target_repo, target_is_directory=True)

    with pytest.raises(ValueError, match="Symlink repository directory rejected"):
        dag.commit(symlink_repo)

    with pytest.raises(ValueError, match="Symlink repository directory rejected"):
        ConversationDAG.load(symlink_repo)

    # 2. Symlink objects directory rejected
    repo_dir = tmp_path / "repo_with_sym_objects"
    repo_dir.mkdir(parents=True, exist_ok=True)
    symlink_objects = repo_dir / "objects"
    symlink_objects.symlink_to(target_repo, target_is_directory=True)

    with pytest.raises(ValueError, match="Symlink objects directory rejected"):
        dag.commit(repo_dir)

    # 3. Symlink HEAD.json rejected
    repo_dir2 = tmp_path / "repo_with_sym_head"
    repo_dir2.mkdir(parents=True, exist_ok=True)
    sens_file = tmp_path / "sensitive.txt"
    sens_file.write_text("sensitive")
    symlink_head = repo_dir2 / "HEAD.json"
    symlink_head.symlink_to(sens_file)

    with pytest.raises(ValueError, match="Symlink HEAD.json rejected"):
        dag.commit(repo_dir2)

    with pytest.raises(ValueError, match="Symlink HEAD.json rejected"):
        ConversationDAG.load(repo_dir2)

    # 4. Symlink blob rejected
    repo_dir3 = tmp_path / "repo_with_sym_blob"
    objects3 = repo_dir3 / "objects"
    objects3.mkdir(parents=True, exist_ok=True)

    # Add message and find hash
    h = dag.nodes[list(dag.nodes.keys())[0]].content_hash
    symlink_blob = objects3 / f"{h}.json"
    symlink_blob.symlink_to(sens_file)

    with pytest.raises(ValueError, match="Symlink blob rejected"):
        dag.commit(repo_dir3)

    # HEAD.json exists for load test
    head_data = {
        'session_id': "session_123",
        'title': "Test Title",
        'version': "v1",
        'nodes': [h],
        'edges': {},
        'roots': [h],
        'id_to_hash': {"m1": h},
        'duplicates': {}
    }
    (repo_dir3 / "HEAD.json").write_text(json.dumps(head_data))
    with pytest.raises(ValueError, match="Symlink blob rejected"):
        ConversationDAG.load(repo_dir3)


def test_conv_versioner_privileges_and_roundtrip(tmp_path):
    repo_dir = tmp_path / "valid_repo"
    dag = ConversationDAG("session_123", "Test Title")
    dag.add_message({"id": "m1", "role": "user", "content": "hello world"})
    dag.add_message({"id": "m2", "role": "assistant", "content": "hello there!", "parent_message_id": "m1"})

    version = dag.commit(repo_dir)
    assert len(version) == 16

    # Verify directory and file permissions
    if os.name != "nt":
        assert (repo_dir.stat().st_mode & 0o777) == 0o700
        assert ((repo_dir / "objects").stat().st_mode & 0o777) == 0o700
        assert ((repo_dir / "HEAD.json").stat().st_mode & 0o777) == 0o600
        for blob in (repo_dir / "objects").glob("*.json"):
            assert (blob.stat().st_mode & 0o777) == 0o600

    # Load and verify roundtrip integrity
    loaded_dag = ConversationDAG.load(repo_dir)
    assert loaded_dag is not None
    assert loaded_dag.session_id == "session_123"
    assert loaded_dag.title == "Test Title"
    assert len(loaded_dag.nodes) == 2
    assert loaded_dag.get_version() == version
