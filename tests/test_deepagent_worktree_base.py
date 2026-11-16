"""Canonical gh_worktree provenance against an isolated local bare remote."""
import subprocess
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "deepcli"))
import deepagent

REAL_SUBPROCESS_RUN = subprocess.run


def git(*args, cwd=None):
    return REAL_SUBPROCESS_RUN(["git", *args], cwd=cwd, check=False, capture_output=True, text=True)


def local_remote(tmp_path, monkeypatch):
    bare = tmp_path / "remote.git"
    git("init", "--bare", str(bare))
    seed = tmp_path / "seed"
    git("clone", str(bare), str(seed))
    git("config", "user.email", "test@example.invalid", cwd=seed)
    git("config", "user.name", "Test", cwd=seed)
    (seed / "tracked.txt").write_text("base\n")
    git("add", "tracked.txt", cwd=seed)
    git("commit", "-m", "initial", cwd=seed)
    git("branch", "-M", "master", cwd=seed)
    git("push", "-u", "origin", "master", cwd=seed)
    git("checkout", "-b", "release/next", cwd=seed)
    git("push", "-u", "origin", "release/next", cwd=seed)
    home = tmp_path / "checkout"
    git("clone", str(bare), str(home))
    git("config", "user.email", "test@example.invalid", cwd=home)
    git("config", "user.name", "Test", cwd=home)
    monkeypatch.setattr(deepagent, "HOME", home)
    monkeypatch.setattr(deepagent, "WORKTREE_ROOT", tmp_path / "worktrees")
    return bare, home


def test_real_create_commit_push_pr_preserves_base_and_remove_cleans_metadata(monkeypatch, tmp_path):
    _, home = local_remote(tmp_path, monkeypatch)
    created = deepagent.DISPATCH["gh_worktree"]({"action": "create", "branch": "feature/provenance", "base": "release/next"})
    assert created["created"] and created["base_recorded"]
    path = Path(created["path"])
    (path / "tracked.txt").write_text("changed\n")
    real_run = subprocess.run
    gh_calls = []

    def stub_gh(cmd, **kwargs):
        if cmd[0] == "gh":
            gh_calls.append(cmd)
            return subprocess.CompletedProcess(cmd, 0, "https://example.invalid/pr/1", "")
        return real_run(cmd, **kwargs)

    monkeypatch.setattr(subprocess, "run", stub_gh)
    result = deepagent.DISPATCH["gh_worktree"]({"action": "commit_push_pr", "branch": "feature/provenance", "repo": "owner/repo", "message": "update"})
    assert result["pr_url"].endswith("/1")
    assert gh_calls[0][gh_calls[0].index("--base") + 1] == "release/next"
    assert git("config", "--local", "--get", "branch.feature/provenance.deepagent-base", cwd=home).stdout.strip() == "release/next"
    removed = deepagent.DISPATCH["gh_worktree"]({"action": "remove", "branch": "feature/provenance"})
    assert removed["removed"] and not removed["base_recorded"]
    assert git("config", "--local", "--get", "branch.feature/provenance.deepagent-base", cwd=home).returncode == 1


def test_explicit_base_overrides_persisted_and_missing_key_falls_back(monkeypatch, tmp_path):
    local_remote(tmp_path, monkeypatch)
    created = deepagent.DISPATCH["gh_worktree"]({"action": "create", "branch": "feature/override", "base": "release/next"})
    Path(created["path"], "tracked.txt").write_text("changed\n")
    real_run, bases = subprocess.run, []

    def stub_gh(cmd, **kwargs):
        if cmd[0] == "gh":
            bases.append(cmd[cmd.index("--base") + 1])
            return subprocess.CompletedProcess(cmd, 0, "ok", "")
        return real_run(cmd, **kwargs)

    monkeypatch.setattr(subprocess, "run", stub_gh)
    assert deepagent.DISPATCH["gh_worktree"]({"action": "commit_push_pr", "branch": "feature/override", "repo": "owner/repo", "message": "x", "base": "explicit"})["pr_url"] == "ok"
    assert bases == ["explicit"]
    # Independent worktree with absent provenance exercises the documented fallback.
    created = deepagent.DISPATCH["gh_worktree"]({"action": "create", "branch": "feature/missing-meta", "base": "release/next"})
    Path(created["path"], "tracked.txt").write_text("changed\n")
    git("config", "--local", "--unset-all", "branch.feature/missing-meta.deepagent-base", cwd=deepagent.HOME)
    deepagent.DISPATCH["gh_worktree"]({"action": "commit_push_pr", "branch": "feature/missing-meta", "repo": "owner/repo", "message": "x"})
    assert bases == ["explicit", "master"]


def test_missing_worktree_and_add_failure(monkeypatch, tmp_path):
    local_remote(tmp_path, monkeypatch)
    missing = deepagent.DISPATCH["gh_worktree"]({"action": "commit_push_pr", "branch": "missing", "repo": "owner/repo"})
    assert "worktree not found" in missing["error"]
    created = deepagent.DISPATCH["gh_worktree"]({"action": "create", "branch": "feature/addfail", "base": "release/next"})
    Path(created["path"], "tracked.txt").write_text("changed\n")
    real = deepagent._wt_git
    calls = []

    def fail_add(args, cwd, timeout=60):
        calls.append(args)
        if args == ["add", "-A"]:
            return subprocess.CompletedProcess(args, 1, "", "denied")
        return real(args, cwd, timeout)

    monkeypatch.setattr(deepagent, "_wt_git", fail_add)
    result = deepagent.DISPATCH["gh_worktree"]({"action": "commit_push_pr", "branch": "feature/addfail", "repo": "owner/repo"})
    assert "git add" in result["error"] and calls[-1] == ["add", "-A"]


def test_fetch_and_metadata_write_failures(monkeypatch, tmp_path):
    local_remote(tmp_path, monkeypatch)
    real = deepagent._wt_git

    def fail_fetch(args, cwd, timeout=60):
        if args[:1] == ["fetch"]:
            return subprocess.CompletedProcess(args, 1, "", "offline")
        return real(args, cwd, timeout)

    monkeypatch.setattr(deepagent, "_wt_git", fail_fetch)
    assert "fetch failed" in deepagent.DISPATCH["gh_worktree"]({"action": "create", "branch": "feature/fetchfail", "base": "release/next"})["error"]
    monkeypatch.setattr(deepagent, "_wt_git", real)

    def fail_write(args, cwd, timeout=60):
        if args[:2] == ["config", "--local"] and "--get" not in args:
            return subprocess.CompletedProcess(args, 1, "", "read only")
        return real(args, cwd, timeout)

    monkeypatch.setattr(deepagent, "_wt_git", fail_write)
    result = deepagent.DISPATCH["gh_worktree"]({"action": "create", "branch": "feature/writefail", "base": "release/next"})
    assert result["created"] and not result["base_recorded"] and Path(result["path"]).is_dir()
    assert "metadata write failed" in result["error"]


def test_metadata_read_failure_precedes_git_add_but_explicit_base_bypasses(monkeypatch, tmp_path):
    local_remote(tmp_path, monkeypatch)
    created = deepagent.DISPATCH["gh_worktree"]({"action": "create", "branch": "feature/readfail", "base": "release/next"})
    Path(created["path"], "tracked.txt").write_text("changed\n")
    real = deepagent._wt_git
    git_actions = []

    def fail_read(args, cwd, timeout=60):
        git_actions.append(args)
        if args[:3] == ["config", "--local", "--get"]:
            return subprocess.CompletedProcess(args, 2, "", "config corrupt")
        return real(args, cwd, timeout)

    monkeypatch.setattr(deepagent, "_wt_git", fail_read)
    err = deepagent.DISPATCH["gh_worktree"]({"action": "commit_push_pr", "branch": "feature/readfail", "repo": "owner/repo"})
    assert "config read failed" in err["error"] and not any(x == ["add", "-A"] for x in git_actions)
    # Explicit base does not read broken provenance.
    monkeypatch.setattr(deepagent, "_wt_git", real)
    monkeypatch.setattr(subprocess, "run", lambda cmd, **kwargs: subprocess.CompletedProcess(cmd, 0, "ok", "") if cmd[0] == "gh" else REAL_SUBPROCESS_RUN(cmd, **kwargs))
    assert deepagent.DISPATCH["gh_worktree"]({"action": "commit_push_pr", "branch": "feature/readfail", "repo": "owner/repo", "base": "explicit"})["pr_url"] == "ok"


def test_remove_retries_metadata_cleanup_after_directory_and_registration_are_gone(monkeypatch, tmp_path):
    local_remote(tmp_path, monkeypatch)
    branch = "feature/cleanup-retry"
    created = deepagent.DISPATCH["gh_worktree"]({"action": "create", "branch": branch, "base": "release/next"})
    real = deepagent._wt_git

    def fail_cleanup(args, cwd, timeout=60):
        if args[:3] == ["config", "--local", "--unset-all"]:
            return subprocess.CompletedProcess(args, 4, "", "config locked")
        return real(args, cwd, timeout)

    monkeypatch.setattr(deepagent, "_wt_git", fail_cleanup)
    first = deepagent.DISPATCH["gh_worktree"]({"action": "remove", "branch": branch})
    assert first["removed"] and first["base_recorded"] and "cleanup failed" in first["error"]
    assert not Path(created["path"]).exists()
    monkeypatch.setattr(deepagent, "_wt_git", real)
    retry = deepagent.DISPATCH["gh_worktree"]({"action": "remove", "branch": branch})
    assert retry == {"removed": True, "branch": branch, "base_recorded": False}
    assert deepagent._wt_base_get(branch) == (None, None)


def test_remove_failure_keeps_metadata_for_existing_or_registered_worktrees(monkeypatch, tmp_path):
    local_remote(tmp_path, monkeypatch)
    branch = "feature/cleanup-guard"
    created = deepagent.DISPATCH["gh_worktree"]({"action": "create", "branch": branch, "base": "release/next"})
    real = deepagent._wt_git
    calls = []

    def fail_remove(args, cwd, timeout=60):
        calls.append(args)
        if args[:2] == ["worktree", "remove"]:
            return subprocess.CompletedProcess(args, 1, "", "worktree locked")
        return real(args, cwd, timeout)

    monkeypatch.setattr(deepagent, "_wt_git", fail_remove)
    first = deepagent.DISPATCH["gh_worktree"]({"action": "remove", "branch": branch})
    assert "worktree remove" in first["error"] and "removed" not in first
    assert not any(args[:3] == ["config", "--local", "--unset-all"] for args in calls)
    # A missing directory alone is insufficient: Git can still register a locked worktree.
    Path(created["path"]).rename(tmp_path / "moved-worktree")
    calls.clear()
    second = deepagent.DISPATCH["gh_worktree"]({"action": "remove", "branch": branch})
    assert "worktree remove" in second["error"] and "removed" not in second
    assert not any(args[:3] == ["config", "--local", "--unset-all"] for args in calls)
    assert deepagent._wt_base_get(branch) == ("release/next", None)
