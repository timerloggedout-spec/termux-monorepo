"""Tests for P2: fragments.py + compose.py (Commit Replay).

Fixture git repo -> extract (gindex) -> fragments (symbol index) ->
compose a NEW file from two fragments in two different source files ->
materialized bytes == expected, py_compile passes, --check verifies.
Run: python3 tests/test_commit_replay_p2.py (or via pytest)
"""
import json, os, py_compile, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CR = os.path.join(ROOT, "scripts", "commit_replay")


def sh(cwd, *args):
    e = dict(os.environ, GIT_AUTHOR_NAME="T", GIT_AUTHOR_EMAIL="t@t",
             GIT_COMMITTER_NAME="T", GIT_COMMITTER_EMAIL="t@t")
    subprocess.run(args, cwd=cwd, env=e, check=True,
                   capture_output=True, text=True)


def run(cwd, script, *args):
    out = subprocess.run([sys.executable, os.path.join(CR, script),
                          *args], cwd=cwd, check=True,
                         capture_output=True, text=True)
    return json.loads(out.stdout)


MOD_A = 'def alpha():\n    return "A"\n\n\ndef beta():\n    return "B"\n'
MOD_B = 'class Gamma:\n    def go(self):\n        return "G"\n'


def test_p2():
    with tempfile.TemporaryDirectory() as d:
        repo = os.path.join(d, "repo")
        os.makedirs(repo)
        sh(repo, "git", "init", "-b", "master", ".")
        open(os.path.join(repo, "a.py"), "w").write(MOD_A)
        open(os.path.join(repo, "b.py"), "w").write(MOD_B)
        sh(repo, "git", "add", "-A")
        sh(repo, "git", "commit", "-m", "fixture")

        idx = os.path.join(d, "idx.jsonl")
        run(repo, "extract.py", "--repo-root", repo, "--repo-name",
            "fixture/repo", "--index", idx)
        frag = os.path.join(d, "frag.jsonl")
        s = run(repo, "fragments.py", "--repo-root", repo, "--repo-name",
                "fixture/repo", "--index", idx, "--out", frag)
        assert s["files"] == 2 and s["fragments"] == 4, s
        recs = [json.loads(l) for l in open(frag) if l.strip()]
        by_sym = {r["symbol"]: r for r in recs if "symbol" in r}
        assert by_sym["beta"]["start_line"] == 5
        assert by_sym["beta"]["end_line"] == 6
        assert by_sym["Gamma"]["kind"] == "class"
        assert by_sym["Gamma.go"]["kind"] == "method"

        def ptr(sym, path):
            r = by_sym[sym]
            return {"path": path, "blob": r["blob"], "symbol": sym,
                    "start_line": r["start_line"],
                    "end_line": r["end_line"]}

        recipe = {"path": "new_mod.py", "segments": [
            {"literal": "# pointer-created fixture\n"},
            ptr("beta", "a.py"),
            {"literal": "\n"},
            ptr("Gamma", "b.py")]}
        rpath = os.path.join(d, "recipe.json")
        json.dump(recipe, open(rpath, "w"))
        out = os.path.join(d, "new_mod.py")
        res = run(repo, "compose.py", "--repo-root", repo, "--recipe",
                  rpath, "--out", out)
        content = open(out).read()
        assert content == ('# pointer-created fixture\n'
                           'def beta():\n    return "B"\n\n'
                           'class Gamma:\n    def go(self):\n'
                           '        return "G"\n'), repr(content)
        py_compile.compile(out, doraise=True)
        chk = run(repo, "compose.py", "--repo-root", repo, "--recipe",
                  rpath, "--out", out, "--check")
        assert chk["matches_file"] is True and chk["sha256"] == res["sha256"]


if __name__ == "__main__":
    test_p2()
    print("ok")
