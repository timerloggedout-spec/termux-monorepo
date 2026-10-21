"""worktree — git-worktree machinery for the agent (CAB Phase B->A port).

Ported from the DeepAgent device lineage (the ~2,000-line on-device
deepagent.py) into the modular recapitulation tree, per the CAB decision:
master's split stays canonical; device-only machinery lands here as its
own module.

What this module carries:
  * branch->base persistence (_wt_bases_load/_wt_bases_save) so
    commit_push_pr opens PRs against the base a worktree was created
    from, not a hardcoded master (the #1067 fix, included in create).
  * the resource-pressure telemetry quartet (_mem_kb, _swap_free_kb,
    _worktree_count, _log_dir_size_mb) plus total/disk/aggregate
    measurements the adaptive gates derive from.
  * hygiene_preflight / post_loop_cleanup with ADAPTIVE gates: limits
    are derived from measured device state (memory/swap totals, free
    disk, average worktree size). Hard numbers survive only as
    documented last-resort defaults for when a measurement is
    unavailable — never as the primary policy.
  * _gh_worktree (create / commit_push_pr / remove / list) with LEAN
    creation: worktrees are created --no-checkout and materialize only
    the caller's task paths via sparse-checkout, because on the origin
    device (BLU B160V) every full checkout materializes a $HOME-sized
    tree. Full checkout is opt-in (full=True).

Retention red line: nothing in this module deletes logs, telemetry, or
training data. Cleanup paths remove git worktrees only; the hygiene
inventory is measurement, not disposal (TrainingData Retention
Preservation protocol).
"""

import os
import pathlib
import shutil
import subprocess

from .runtime import HOME, WORKTREE_ROOT, _wt_default_repo, _wt_git, _wt_safe

_WT_BASE_FILE = HOME / ".deepcli" / "watchdog" / "worktree-bases.json"

# Last-resort defaults, used ONLY when the corresponding measurement is
# unavailable. The adaptive derivations in _adaptive_limits() are the
# policy; these constants are the documented fallback (they preserve the
# device lineage's original hard-written values as the floor behavior).
_DEFAULT_MEM_FLOOR_MB = 300
_DEFAULT_SWAP_FLOOR_MB = 150
_DEFAULT_WORKTREE_CEILING = 50
# Fraction of currently-free disk the worktree inventory may occupy
# before the ceiling derived from it starts refusing new runs.
_DISK_BUDGET_FRACTION = 0.25
# Floors as fractions of measured totals (adaptive replacements for the
# lineage's absolute 300MB / 150MB writes).
_MEM_FLOOR_FRACTION = 0.06
_SWAP_FLOOR_FRACTION = 0.10


# --------------------------------------------------------------------- #
# branch -> base persistence (#1067)
# --------------------------------------------------------------------- #
def _wt_bases_load():
    import json as _j

    try:
        return _j.loads(_WT_BASE_FILE.read_text())
    except Exception:
        return {}


def _wt_bases_save(d):
    import json as _j

    _WT_BASE_FILE.parent.mkdir(parents=True, exist_ok=True)
    _WT_BASE_FILE.write_text(_j.dumps(d))


def _wt_default_repo_branch() -> str | None:
    """Branch the PR should target by default (origin/HEAD)."""
    r = _wt_git(["symbolic-ref", "--short", "refs/remotes/origin/HEAD"], str(HOME))
    if r.returncode == 0 and r.stdout.strip():
        return r.stdout.strip().rsplit("/", 1)[-1]
    return None


# --------------------------------------------------------------------- #
# resource-pressure telemetry
# --------------------------------------------------------------------- #
def _meminfo_kb(field):
    try:
        for line in pathlib.Path("/proc/meminfo").read_text().splitlines():
            if line.startswith(field + ":"):
                return int(line.split()[1])
    except Exception:
        pass
    return -1


def _mem_kb():
    kb = _meminfo_kb("MemAvailable")
    return kb if kb >= 0 else 999_999_999


def _mem_total_kb():
    return _meminfo_kb("MemTotal")


def _swap_free_kb():
    kb = _meminfo_kb("SwapFree")
    return kb if kb >= 0 else 999_999_999


def _swap_total_kb():
    return _meminfo_kb("SwapTotal")


def _disk_free_mb():
    try:
        return shutil.disk_usage(str(HOME)).free // (1024 * 1024)
    except Exception:
        return -1


def _worktree_count():
    try:
        r = subprocess.run(
            ["git", "-C", str(HOME), "worktree", "list", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return sum(1 for l in r.stdout.splitlines() if l.startswith("worktree "))
    except Exception:
        return -1


def _worktree_bytes_mb():
    """Aggregate on-disk size of all registered worktrees (-1 if unknown)."""
    try:
        r = subprocess.run(
            ["git", "-C", str(HOME), "worktree", "list", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if r.returncode != 0:
            return -1
        total = 0
        for line in r.stdout.splitlines():
            if not line.startswith("worktree "):
                continue
            root = pathlib.Path(line[9:])
            for p in root.rglob("*"):
                try:
                    if p.is_file() and not p.is_symlink():
                        total += p.stat().st_size
                except Exception:
                    pass
        return total // (1024 * 1024)
    except Exception:
        return -1


def _log_dir_size_mb():
    try:
        total = 0
        for p in (HOME / ".deepcli" / "logs").rglob("*"):
            if p.is_file():
                total += p.stat().st_size
        return total // (1024 * 1024)
    except Exception:
        return -1


# --------------------------------------------------------------------- #
# adaptive hygiene gates
# --------------------------------------------------------------------- #
def _adaptive_limits():
    """Derive gate limits from measured device state.

    Returns (limits, basis): limits has mem_floor_mb, swap_floor_mb,
    worktree_ceiling; basis explains, per limit, the measurement it was
    derived from or that the documented default was used.
    """
    basis = {}

    mem_total_mb = _mem_total_kb() // 1024
    if mem_total_mb > 0:
        mem_floor = int(mem_total_mb * _MEM_FLOOR_FRACTION)
        basis["mem_floor_mb"] = (
            f"{_MEM_FLOOR_FRACTION:.0%} of measured MemTotal {mem_total_mb}MB"
        )
    else:
        mem_floor = _DEFAULT_MEM_FLOOR_MB
        basis["mem_floor_mb"] = "default (MemTotal unmeasurable)"

    swap_total_kb = _swap_total_kb()
    swap_total_mb = swap_total_kb // 1024
    if swap_total_kb == 0:
        # No swap configured on this device: a swap-free floor is
        # meaningless and would refuse every run. Gate inapplicable.
        swap_floor = 0
        basis["swap_floor_mb"] = "inapplicable (no swap configured)"
    elif swap_total_mb > 0:
        swap_floor = int(swap_total_mb * _SWAP_FLOOR_FRACTION)
        basis["swap_floor_mb"] = (
            f"{_SWAP_FLOOR_FRACTION:.0%} of measured SwapTotal {swap_total_mb}MB"
        )
    else:
        swap_floor = _DEFAULT_SWAP_FLOOR_MB
        basis["swap_floor_mb"] = "default (SwapTotal unmeasurable)"

    disk_free_mb = _disk_free_mb()
    wt = _worktree_count()
    wt_bytes = _worktree_bytes_mb()
    avg_wt_mb = (wt_bytes / wt) if (wt and wt > 0 and wt_bytes and wt_bytes > 0) else -1
    if disk_free_mb > 0 and avg_wt_mb > 0:
        ceiling = int((disk_free_mb * _DISK_BUDGET_FRACTION) // avg_wt_mb)
        ceiling = max(1, ceiling)
        basis["worktree_ceiling"] = (
            f"{_DISK_BUDGET_FRACTION:.0%} of {disk_free_mb}MB free disk "
            f"/ avg worktree {avg_wt_mb:.0f}MB"
        )
    else:
        ceiling = _DEFAULT_WORKTREE_CEILING
        basis["worktree_ceiling"] = "default (disk or worktree size unmeasurable)"

    limits = {
        "mem_floor_mb": mem_floor,
        "swap_floor_mb": swap_floor,
        "worktree_ceiling": ceiling,
    }
    return limits, basis


def hygiene_preflight(verbose=True):
    """Return dict; refuse if environment unsafe. Non-destructive.

    Gates are adaptive: floors and the worktree ceiling come from
    _adaptive_limits() (measured device pressure), not hard writes.
    """
    mem_mb = _mem_kb() // 1024
    swap_mb = _swap_free_kb() // 1024
    wt = _worktree_count()
    log_mb = _log_dir_size_mb()
    limits, basis = _adaptive_limits()
    state = {
        "mem_available_mb": mem_mb,
        "swap_free_mb": swap_mb,
        "worktrees": wt,
        "log_dir_mb": log_mb,
        "limits": limits,
        "limits_basis": basis,
        "ok": True,
        "reasons": [],
    }
    if mem_mb < limits["mem_floor_mb"]:
        state["ok"] = False
        state["reasons"].append(
            f"mem_available={mem_mb}MB < floor {limits['mem_floor_mb']}MB "
            f"({basis['mem_floor_mb']})"
        )
    if swap_mb < limits["swap_floor_mb"]:
        state["ok"] = False
        state["reasons"].append(
            f"swap_free={swap_mb}MB < floor {limits['swap_floor_mb']}MB "
            f"({basis['swap_floor_mb']})"
        )
    if wt > limits["worktree_ceiling"]:
        state["ok"] = False
        state["reasons"].append(
            f"worktrees={wt} > ceiling {limits['worktree_ceiling']} "
            f"({basis['worktree_ceiling']}) — inventory cleanup required"
        )
    if verbose:
        print(
            f"  [hygiene] mem={mem_mb}MB swap={swap_mb}MB worktrees={wt} logs={log_mb}MB"
        )
        for r in state["reasons"]:
            print(f"  [hygiene] REFUSE: {r}")
    return state


def post_loop_cleanup():
    """Non-destructive: log inventory, no deletion.

    Retention red line: this reports worktree/log inventory only. It
    must never delete logs, telemetry, or training data.
    """
    try:
        wt = _worktree_count()
        log_mb = _log_dir_size_mb()
        mem_mb = _mem_kb() // 1024
        print(f"  [hygiene-post] mem={mem_mb}MB worktrees={wt} logs={log_mb}MB")
    except Exception:
        pass


# --------------------------------------------------------------------- #
# gh_worktree tool (lean create; #1027 fixes + #1067 persistence)
# --------------------------------------------------------------------- #
def _gh_worktree(a):
    action = a.get("action", "")
    WORKTREE_ROOT.mkdir(parents=True, exist_ok=True)
    repo_root = str(WORKTREE_ROOT.parent.parent)

    if action == "list":
        r = _wt_git(["worktree", "list", "--porcelain"], repo_root)
        if r.returncode != 0:
            return {"error": r.stderr[-400:]}
        entries = []
        cur = {}
        for line in r.stdout.splitlines():
            if line.startswith("worktree "):
                if cur:
                    entries.append(cur)
                cur = {"path": line[9:]}
            elif line.startswith("branch "):
                cur["branch"] = line[7:]
        if cur:
            entries.append(cur)
        return {"worktrees": entries}

    if action == "create":
        branch = a.get("branch") or ""
        base = a.get("base") or "master"
        if not branch:
            return {"error": "branch required"}
        safe = _wt_safe(branch)
        path = WORKTREE_ROOT / safe
        if path.exists():
            return {"error": f"worktree already exists: {path}", "path": str(path)}

        # fetch base
        r = _wt_git(["fetch", "origin", base], repo_root, timeout=120)
        if r.returncode != 0:
            return {"error": f"fetch failed: {r.stderr[-300:]}"}

        # LEAN create: --no-checkout so no $HOME-sized tree materializes;
        # sparse-checkout then materializes only the task paths (if any).
        # full=True opts into a complete checkout explicitly.
        full = bool(a.get("full"))
        paths = a.get("paths") or []
        add_args = ["worktree", "add"]
        if not full:
            add_args.append("--no-checkout")
        add_args += ["-b", branch, str(path), f"origin/{base}"]
        r = _wt_git(add_args, repo_root, timeout=120)
        if r.returncode != 0:
            return {"error": f"worktree add failed: {r.stderr[-300:]}"}
        materialized = "full" if full else "none"
        if not full and paths:
            r = _wt_git(
                ["sparse-checkout", "set", "--no-cone", *paths], str(path)
            )
            if r.returncode != 0:
                return {"error": f"sparse-checkout failed: {r.stderr[-300:]}"}
            r = _wt_git(["checkout"], str(path))
            if r.returncode != 0:
                return {"error": f"checkout failed: {r.stderr[-300:]}"}
            materialized = "sparse"
        # Persist branch->base so commit_push_pr opens the PR against the
        # base this worktree was created from (not the hardcoded master).
        try:
            _b = _wt_bases_load()
            _b[branch] = base
            _wt_bases_save(_b)
        except Exception:
            pass
        return {
            "path": str(path),
            "branch": branch,
            "base": base,
            "created": True,
            "materialized": materialized,
            "paths": paths,
        }

    if action == "commit_push_pr":
        branch = a.get("branch") or ""
        message = a.get("message") or "update via agent"
        title = a.get("title") or message.split("\n")[0][:200]
        body = a.get("body") or message
        repo = a.get("repo") or _wt_default_repo()
        # coerce all string fields; nested dicts leak from malformed model output
        for _k in ("message", "title", "body", "base", "branch", "repo"):
            _v = a.get(_k)
            if _v is not None and not isinstance(_v, str):
                a[_k] = str(_v)
        draft = bool(a.get("draft"))
        if not branch or not repo:
            return {"error": "branch and repo required"}
        safe = _wt_safe(branch)
        path = WORKTREE_ROOT / safe
        if not path.exists():
            return {"error": f"worktree not found: {path}"}

        # stage and commit — exclude auto-generated sweep-ledger files
        _EXCLUDE = (".git", "docs/ops/generated/sweep-ledger", "docs/ops/generated/")
        r = _wt_git(["add", "-A", "--", "."], str(path))
        # unstage anything under excluded paths
        for _ex in _EXCLUDE[1:]:
            _wt_git(["reset", "-q", "HEAD", "--", _ex], str(path))
        if r.returncode != 0:
            return {"error": f"git add: {r.stderr[-300:]}"}
        r = _wt_git(["status", "--porcelain"], str(path))
        if not r.stdout.strip():
            return {"error": "no changes to commit"}
        r = _wt_git(["commit", "-m", message], str(path), timeout=120)
        if r.returncode != 0:
            return {"error": f"git commit: {r.stderr[-300:]}"}

        # push branch
        r = _wt_git(["push", "-u", "origin", branch], str(path), timeout=180)
        if r.returncode != 0:
            return {"error": f"git push: {r.stderr[-400:]}"}

        # create PR via gh
        # default PR base to the base the worktree was created from
        _b = _wt_bases_load()
        _default_base = a.get("base") or _b.get(branch) or _wt_default_repo_branch() or "master"
        pr_cmd = [
            "gh",
            "pr",
            "create",
            "--repo",
            repo,
            "--base",
            _default_base,
            "--head",
            branch,
            "--title",
            title,
            "--body",
            body,
        ]
        if draft:
            pr_cmd.append("--draft")
        r = subprocess.run(pr_cmd, capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            return {"error": f"gh pr create: {r.stderr[-400:]}", "commit_pushed": True}
        return {
            "pr_url": r.stdout.strip(),
            "branch": branch,
            "commit_pushed": True,
            "repo": repo,
        }

    if action == "remove":
        branch = a.get("branch") or ""
        force = bool(a.get("force", True))
        if not branch:
            return {"error": "branch required"}
        safe = _wt_safe(branch)
        path = WORKTREE_ROOT / safe
        args = ["worktree", "remove", str(path)]
        if force:
            args.append("--force")
        r = _wt_git(args, repo_root, timeout=60)
        if r.returncode != 0:
            return {"error": f"worktree remove: {r.stderr[-300:]}"}
        # also forget the persisted base mapping for the removed branch
        try:
            _b = _wt_bases_load()
            if branch in _b:
                del _b[branch]
                _wt_bases_save(_b)
        except Exception:
            pass
        return {"removed": True, "branch": branch}

    return {"error": f"unknown action: {action}. Use create|commit_push_pr|remove|list"}
