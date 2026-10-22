#!/usr/bin/env python3
"""Create a bounded, sparse Antigravity collaboration worktree (local Git only)."""
from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SPARSE_PATHS = (
    "scripts/antigravity",
    "tests",
    "docs/proposals/active/antigravity-cli-provisioning",
    "docs/icm/processes",
    "docs/ci",
    ".agents/skills/agy-bounded-collaboration",
)
BRANCH_RE = re.compile(r"cue/1497-[a-z0-9]+(?:-[a-z0-9]+)*\Z")

class PlanError(ValueError):
    pass

def git(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and result.returncode:
        raise PlanError(result.stderr.strip() or f"git {args[0]} failed")
    return result.stdout.strip()

def config_values(repo: Path, key: str) -> list[str]:
    result = subprocess.run(["git", "-C", str(repo), "config", "--local", "--get-all", key],
                            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode not in (0, 1):
        raise PlanError(result.stderr.strip() or f"unable to read {key}")
    return result.stdout.splitlines()

def common_git_dir(repo: Path) -> Path:
    raw = git(repo, "rev-parse", "--git-common-dir")
    p = Path(raw)
    return (repo / p).resolve() if not p.is_absolute() else p.resolve()

def shared_extension_enabled(repo: Path) -> bool:
    vals = config_values(repo, "extensions.worktreeConfig")
    return bool(vals and vals[-1].lower() == "true")

def ensure_safe_to_enable(repo: Path) -> None:
    for key in ("core.worktree", "core.sparseCheckout", "core.sparseCheckoutCone"):
        if config_values(repo, key):
            raise PlanError(f"cannot enable extensions.worktreeConfig: shared {key} is configured")
    if any(v.lower() == "true" for v in config_values(repo, "core.bare")):
        raise PlanError("cannot enable extensions.worktreeConfig: shared core.bare is true")
    common = common_git_dir(repo)
    candidates = [common / "config.worktree"]
    worktrees = common / "worktrees"
    if worktrees.is_dir():
        candidates.extend(p / "config.worktree" for p in worktrees.iterdir() if p.is_dir())
    if any(p.exists() for p in candidates):
        raise PlanError("cannot enable extensions.worktreeConfig: dormant config.worktree exists")

def make_plan(repo_arg: str, destination_arg: str, branch: str, base: str,
              enable_worktree_config: bool = False) -> dict:
    repo_input = Path(repo_arg).expanduser().absolute()
    if repo_input.is_symlink():
        raise PlanError("repository path must not be a symlink")
    repo = Path(git(repo_input, "rev-parse", "--show-toplevel")).resolve()
    dest_input = Path(destination_arg).expanduser().absolute()
    if dest_input.exists() or dest_input.is_symlink():
        raise PlanError("destination must not already exist (including a symlink)")
    if any(p.is_symlink() for p in dest_input.parents):
        raise PlanError("destination path contains a symlink")
    dest = dest_input.parent.resolve() / dest_input.name
    if dest == repo or repo in dest.parents or dest in repo.parents:
        raise PlanError("destination must be outside and not nested with the source repository")
    if not BRANCH_RE.fullmatch(branch):
        raise PlanError("branch must match cue/1497-<lowercase-hyphenated-name>")
    if git(repo, "check-ref-format", "--branch", branch, check=False) == "":
        raise PlanError("invalid branch name")
    if subprocess.run(["git", "-C", str(repo), "show-ref", "--verify", "--quiet",
                       f"refs/heads/{branch}"]).returncode == 0:
        raise PlanError("branch already exists")
    if not re.fullmatch(r"[0-9a-fA-F]{40}", base):
        raise PlanError("base must be a full 40-character commit SHA")
    resolved = git(repo, "rev-parse", "--verify", base + "^{commit}", check=False)
    if resolved.lower() != base.lower():
        raise PlanError("base SHA does not resolve locally to that commit")
    enabled = shared_extension_enabled(repo)
    if not enabled:
        ensure_safe_to_enable(repo)
    return {"repo": str(repo), "destination": str(dest), "branch": branch,
            "base_sha": resolved, "sparse_paths": list(SPARSE_PATHS),
            "apply": False, "runtime_verified": False,
            "worktree_config": {"shared_extension_enabled": enabled,
                                 "enable_required": not enabled,
                                 "enable_opt_in": enable_worktree_config,
                                 "shared_extension_will_change": not enabled and enable_worktree_config},
            "isolation": "Git worktree and sparse checkout only; not an OS sandbox"}

def apply_plan(plan: dict, enable_worktree_config: bool = False) -> None:
    repo, dest = Path(plan["repo"]), Path(plan["destination"])
    if plan["worktree_config"]["enable_required"] and not enable_worktree_config:
        raise PlanError("apply requires --enable-worktree-config to modify shared Git config")
    try:
        if plan["worktree_config"]["enable_required"]:
            ensure_safe_to_enable(repo)
            git(repo, "config", "--local", "extensions.worktreeConfig", "true")
        git(repo, "worktree", "add", "--no-checkout", "-b", plan["branch"], str(dest), plan["base_sha"])
        git(dest, "sparse-checkout", "init", "--cone")
        git(dest, "sparse-checkout", "set", "--cone", *SPARSE_PATHS)
        git(dest, "read-tree", "-mu", "HEAD")
    except Exception as exc:
        plan["apply"] = True
        plan["partial_failure"] = str(exc)
        plan["recovery_state"] = {
            "destination_exists": dest.exists(), "branch_exists": subprocess.run(
                ["git", "-C", str(repo), "show-ref", "--verify", "--quiet", f"refs/heads/{plan['branch']}"]).returncode == 0,
            "action": "No automatic cleanup was attempted; inspect the destination and branch, then manually complete or remove them.",
        }
        print(json.dumps(plan, ensure_ascii=False, indent=2), file=sys.stderr)
        raise
    plan["apply"] = True
    plan["worktree_created"] = True
    plan["runtime_verified"] = False

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="existing local Git repository")
    parser.add_argument("--destination", required=True, help="new worktree path outside repo")
    parser.add_argument("--branch", required=True, help="new cue/1497-* branch")
    parser.add_argument("--base", required=True, help="locally available full 40-character commit SHA")
    parser.add_argument("--apply", action="store_true", help="create the worktree; default only prints a plan")
    parser.add_argument("--enable-worktree-config", action="store_true",
                        help="explicitly allow enabling shared extensions.worktreeConfig if absent/false")
    args = parser.parse_args(argv)
    try:
        plan = make_plan(args.repo, args.destination, args.branch, args.base, args.enable_worktree_config)
        if args.apply:
            apply_plan(plan, args.enable_worktree_config)
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0
    except (PlanError, OSError, subprocess.SubprocessError) as exc:
        print(json.dumps({"error": str(exc), "runtime_verified": False}, ensure_ascii=False), file=sys.stderr)
        return 2
    except Exception:
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
