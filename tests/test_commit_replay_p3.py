"""Tests for P3 jit_resolve (scripts/commit_replay/jit.py).

Fixture (shared shape w/ P2): 2 py files -> extract -> fragments ->
symbol-only recipe -> jit resolve -> compose == hand-built expectation.
Also: ambiguity (same symbol in 2 files) resolves deterministically and
reports candidates=2; missing symbol fails closed (exit 1).
Run: python3 tests/test_commit_replay_p3.py (or via pytest)
"""
import json, os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CR = os.path.join(ROOT, "scripts", "commit_replay")
MOD_A = 'def shared():\n    return "A"\n\n\ndef only_a():\n    return 1\n'
MOD_B = 'def shared():\n    return "B"\n'


def sh(cwd, *args):
    e = dict(os.environ, GIT_AUTHOR_NAME="T", GIT_AUTHOR_EMAIL="t@t",
             GIT_COMMITTER_NAME="T", GIT_COMMITTER_EMAIL="t@t")
    subprocess.run(args, cwd=cwd, env=e, check=True,
                   capture_output=True, text=True)


def run(cwd, script, *args, expect=0):
    out = subprocess.run([sys.executable, os.path.join(CR, script),
                          *args], cwd=cwd, capture_output=True, text=True)
    assert out.returncode == expect, (script, out.returncode, out.stderr)
    return json.loads(out.stdout) if out.stdout.strip() else {}


def test_p3():
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
        run(repo, "fragments.py", "--repo-root", repo, "--repo-name",
            "fixture/repo", "--index", idx, "--out", frag)

        # single-symbol lookup: unique + ambiguous
        r = run(repo, "jit.py", "--fragments", frag, "--symbol", "only_a")
        assert r["resolved"]["only_a"]["path"] == "a.py"
        assert r["resolved"]["only_a"]["candidates"] == 1
        r = run(repo, "jit.py", "--fragments", frag, "--symbol", "shared")
        assert r["resolved"]["shared"]["candidates"] == 2
        assert r["resolved"]["shared"]["path"] == "a.py"  # sorted-first
        # missing symbol fails closed
        run(repo, "jit.py", "--fragments", frag, "--symbol", "nope",
            expect=1)

        # symbol-only recipe -> resolve -> compose
        recipe = {"path": "out.py", "segments": [
            {"symbol": "shared", "path": "b.py"},
            {"literal": "\n"},
            {"symbol": "only_a"}]}
        rp = os.path.join(d, "r.json")
        json.dump(recipe, open(rp, "w"))
        res = run(repo, "jit.py", "--fragments", frag, "--recipe", rp)
        assert len(res["report"]) == 2
        out = os.path.join(d, "out.py")
        run(repo, "compose.py", "--repo-root", repo, "--recipe", rp,
            "--out", out)
        assert open(out).read() == ('def shared():\n    return "B"\n\n'
                                    'def only_a():\n    return 1\n')


if __name__ == "__main__":
    test_p3()
    print("ok")
