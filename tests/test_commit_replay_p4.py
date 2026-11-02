"""Tests for P4 edit() (scripts/commit_replay/edit.py).

Pure recipe transforms (no git needed for replace/drop/reorder/insert/
customize) + one end-to-end: edit a symbol recipe, jit-resolve, compose,
bytes == expectation; lineage records the parent recipe hash.
Run: python3 tests/test_commit_replay_p4.py (or via pytest)
"""
import hashlib, json, os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CR = os.path.join(ROOT, "scripts", "commit_replay")
L = lambda s: {"literal": s}  # noqa: E731
P = lambda sym: {"symbol": sym}  # noqa: E731


def run(script, *args, cwd=None):
    out = subprocess.run([sys.executable, os.path.join(CR, script),
                          *args], cwd=cwd, check=True,
                         capture_output=True, text=True)
    return json.loads(out.stdout)


def edit(d, recipe, ops, name="r"):
    rp = os.path.join(d, name + ".json")
    op = os.path.join(d, name + "-ops.json")
    json.dump(recipe, open(rp, "w"))
    json.dump({"ops": ops}, open(op, "w"))
    outp = os.path.join(d, name + "-v2.json")
    run("edit.py", "--recipe", rp, "--ops", op, "--out", outp)
    return json.load(open(outp)), rp


def test_ops():
    with tempfile.TemporaryDirectory() as d:
        base = {"path": "x.py", "segments": [L("a"), P("s1"), L("b")]}
        r, rp = edit(d, base, [{"op": "replace", "segment": 0,
                                "with": L("A")}])
        assert [s.get("literal") for s in r["segments"]] == \
            ["A", None, "b"]
        parent = hashlib.sha256(open(rp, "rb").read()).hexdigest()
        assert r["lineage"][0]["parent_recipe_sha256"] == parent
        r2, _ = edit(d, base, [{"op": "drop", "segment": 1}])
        assert len(r2["segments"]) == 2
        r3, _ = edit(d, base, [{"op": "insert", "at": "after",
                                "segment": 0, "with": L("x")}])
        assert [s.get("literal") for s in r3["segments"][:2]] == \
            ["a", "x"]
        r4, _ = edit(d, base, [{"op": "reorder", "order": [2, 1, 0]}])
        assert r4["segments"][0] == L("b")
        ptr = {"path": "f.py", "blob": "0" * 40, "symbol": "f",
               "start_line": 1, "end_line": 9}
        r5, _ = edit(d, {"path": "y.py", "segments": [ptr]},
                     [{"op": "customize", "segment": 0,
                       "set": {"end_line": 5}}])
        assert r5["segments"][0]["end_line"] == 5
        # chained edit extends lineage
        rp2 = os.path.join(d, "chain.json")
        json.dump(r, open(rp2, "w"))
        op2 = os.path.join(d, "chain-ops.json")
        json.dump({"ops": [{"op": "drop", "segment": 2}]}, open(op2, "w"))
        run("edit.py", "--recipe", rp2, "--ops", op2)
        assert len(json.load(open(rp2))["lineage"]) == 2


def test_end_to_end():
    with tempfile.TemporaryDirectory() as d:
        repo = os.path.join(d, "repo")
        os.makedirs(repo)
        e = dict(os.environ, GIT_AUTHOR_NAME="T", GIT_AUTHOR_EMAIL="t@t",
                 GIT_COMMITTER_NAME="T", GIT_COMMITTER_EMAIL="t@t")
        def sh(*args):
            subprocess.run(args, cwd=repo, env=e, check=True,
                           capture_output=True, text=True)
        sh("git", "init", "-b", "master", ".")
        open(os.path.join(repo, "m.py"), "w").write(
            'def keep():\n    return "K"\n\n\ndef gone():\n    return "X"\n')
        sh("git", "add", "-A")
        sh("git", "commit", "-m", "fixture")
        idx = os.path.join(d, "idx.jsonl")
        run("extract.py", "--repo-root", repo, "--repo-name",
            "fixture/repo", "--index", idx, cwd=repo)
        frag = os.path.join(d, "frag.jsonl")
        run("fragments.py", "--repo-root", repo, "--repo-name",
            "fixture/repo", "--index", idx, "--out", frag, cwd=repo)
        recipe = {"path": "o.py", "segments": [P("keep"), L("\n"),
                                               P("gone")]}
        edited, _ = edit(d, recipe, [{"op": "drop", "segment": 2},
                                     {"op": "drop", "segment": 1}])
        ep = os.path.join(d, "edited.json")
        json.dump(edited, open(ep, "w"))
        run("jit.py", "--fragments", frag, "--recipe", ep, cwd=repo)
        out = os.path.join(d, "o.py")
        run("compose.py", "--repo-root", repo, "--recipe", ep,
            "--out", out, cwd=repo)
        assert open(out).read() == 'def keep():\n    return "K"\n'


def test_lineage_check():
    """§9 condition: compose --check verifies lineage parent hashes
    against sibling recipe files; missing parent = fail-closed."""
    with tempfile.TemporaryDirectory() as d:
        repo = os.path.join(d, "repo")
        os.makedirs(repo)
        e = dict(os.environ, GIT_AUTHOR_NAME="T", GIT_AUTHOR_EMAIL="t@t",
                 GIT_COMMITTER_NAME="T", GIT_COMMITTER_EMAIL="t@t")

        def sh(*args):
            subprocess.run(args, cwd=repo, env=e, check=True,
                           capture_output=True, text=True)
        sh("git", "init", "-b", "master", ".")
        open(os.path.join(repo, "m.py"), "w").write(
            'def keep():\n    return "K"\n')
        sh("git", "add", "-A")
        sh("git", "commit", "-m", "fixture")
        idx = os.path.join(d, "idx.jsonl")
        run("extract.py", "--repo-root", repo, "--repo-name",
            "fixture/repo", "--index", idx, cwd=repo)
        frag = os.path.join(d, "frag.jsonl")
        run("fragments.py", "--repo-root", repo, "--repo-name",
            "fixture/repo", "--index", idx, "--out", frag, cwd=repo)
        rdir = os.path.join(d, "recipes")
        os.makedirs(rdir)
        parent = {"path": "o.py", "segments": [P("keep")]}
        pp = os.path.join(rdir, "parent.json")
        json.dump(parent, open(pp, "w"))
        edit(rdir, parent,
             [{"op": "insert", "at": "after", "segment": 0,
               "with": L("\n")}], name="child")
        # parent copy sits at child.json; edited recipe at child-v2.json,
        # same directory => lineage parent hash resolvable by compose
        ep = os.path.join(rdir, "child-v2.json")
        run("jit.py", "--fragments", frag, "--recipe", ep, cwd=repo)
        # NOTE: jit rewrites ep in place; lineage survives (dict passthrough)
        out = os.path.join(d, "o.py")
        run("compose.py", "--repo-root", repo, "--recipe", ep,
            "--out", out, cwd=repo)
        chk = run("compose.py", "--repo-root", repo, "--recipe", ep,
                  "--out", out, "--check", cwd=repo)
        assert chk["lineage"] == {"depth": 1, "verified": 1, "ok": True}, chk
        # tamper: point lineage at a nonexistent parent hash -> exit 1
        bad = json.load(open(ep))
        bad["lineage"][0]["parent_recipe_sha256"] = "0" * 64
        json.dump(bad, open(ep, "w"))
        res = subprocess.run(
            [sys.executable, os.path.join(CR, "compose.py"),
             "--repo-root", repo, "--recipe", ep, "--out", out,
             "--check"], capture_output=True, text=True)
        assert res.returncode == 1, res.stdout


if __name__ == "__main__":
    test_ops()
    test_end_to_end()
    test_lineage_check()
    print("ok")
