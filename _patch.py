import io

P = "deepcli/deepagent.py"
src = io.open(P, encoding="utf-8").read()
orig = src

# Fix 1: the set-literal-in-except TypeError
old1 = "    try: return _j.loads(_WT_BASE_FILE.read_text())\n    except Exception: return {{}}\n"
new1 = "    try: return _j.loads(_WT_BASE_FILE.read_text())\n    except Exception: return {}\n"
assert src.count(old1) == 1, ("fix1 count", src.count(old1))
src = src.replace(old1, new1)

# Fix 3: define the missing _wt_default_repo_branch() used at the PR-open step.
old3 = 'def _gh_worktree(a):\n    action = a.get("action", "")'
new3 = (
    "def _wt_default_repo_branch() -> str | None:\n"
    '    """Branch the PR should target by default (origin/HEAD)."""\n'
    '    r = _wt_git(["symbolic-ref", "--short", "refs/remotes/origin/HEAD"], str(HOME))\n'
    "    if r.returncode == 0 and r.stdout.strip():\n"
    '        return r.stdout.strip().rsplit("/", 1)[-1]\n'
    "    return None\n"
    "\n"
    "\n"
    "def _gh_worktree(a):\n"
    '    action = a.get("action", "")'
)
assert src.count(old3) == 1, ("fix3 count", src.count(old3))
src = src.replace(old3, new3)

# Fix 2: persist base provenance in the create branch so the map accumulates.
old2 = '        return {"path": str(path), "branch": branch, "base": base, "created": True}'
new2 = (
    "        try:\n"
    "            _b = _wt_bases_load()\n"
    "            _b[branch] = base\n"
    "            _wt_bases_save(_b)\n"
    "        except Exception:\n"
    "            pass\n"
    '        return {"path": str(path), "branch": branch, "base": base, "created": True}'
)
assert src.count(old2) == 1, ("fix2 count", src.count(old2))
src = src.replace(old2, new2)

assert src != orig
io.open(P, "w", encoding="utf-8").write(src)
print("patched: 3 fixes applied")
