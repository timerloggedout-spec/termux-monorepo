"""Tests for scripts/commit_replay/extract.py (Commit Replay P1).

Builds a tiny fixture git repo (2 branches + tag, add/modify/delete),
runs extract twice (2nd run must be a no-op), and derives the reverse
index + path_history in-test to prove the entry records carry them.
Run: python3 -m pytest tests/test_commit_replay_extract.py -q
     or plain: python3 tests/test_commit_replay_extract.py
"""
import json, os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTRACT = os.path.join(ROOT, "scripts", "commit_replay", "extract.py")


def sh(cwd, *args, env=None):
    e = dict(os.environ, GIT_AUTHOR_NAME="T", GIT_AUTHOR_EMAIL="t@t",
             GIT_COMMITTER_NAME="T", GIT_COMMITTER_EMAIL="t@t")
    if env:
        e.update(env)
    subprocess.run(args, cwd=cwd, env=e, check=True,
                   capture_output=True, text=True)


def run_extract(repo, index, *extra):
    out = subprocess.run([sys.executable, EXTRACT, "--repo-root", repo,
                          "--repo-name", "fixture/repo", "--index", index,
                          *extra], check=True, capture_output=True, text=True)
    return json.loads(out.stdout)


def load(index):
    recs = [json.loads(l) for l in open(index, encoding="utf-8") if l.strip()]
    hdr = recs[0]
    commits = {r["oid"]: r for r in recs if r.get("kind") == "commit"}
    entries = [r for r in recs if r.get("kind") == "entry"]
    return hdr, commits, entries


def build_fixture(d):
    repo = os.path.join(d, "repo")
    os.makedirs(repo)
    sh(repo, "git", "init", "-b", "master", ".")
    open(os.path.join(repo, "a.txt"), "w").write("one\n")
    open(os.path.join(repo, "b.txt"), "w").write("bee\n")
    sh(repo, "git", "add", "-A")
    sh(repo, "git", "commit", "-m", "c1 add a+b")
    open(os.path.join(repo, "a.txt"), "w").write("one\ntwo\n")
    os.remove(os.path.join(repo, "b.txt"))
    sh(repo, "git", "add", "-A")
    sh(repo, "git", "commit", "-m", "c2 modify a, delete b")
    sh(repo, "git", "tag", "v0")
    sh(repo, "git", "checkout", "-b", "side")
    open(os.path.join(repo, "c.txt"), "w").write("see\n")
    sh(repo, "git", "add", "-A")
    sh(repo, "git", "commit", "-m", "c3 side adds c")
    return repo


def test_extract_incremental_and_derivable():
    with tempfile.TemporaryDirectory() as d:
        repo = build_fixture(d)
        index = os.path.join(d, "idx.jsonl")
        s1 = run_extract(repo, index)
        assert s1["new"] == 3 and s1["commits"] == 3, s1
        hdr, commits, entries = load(index)
        assert hdr["spec"] == "commit-store/v1"
        assert hdr["commits_indexed"] == 3
        assert set(hdr["checkpoints"]) == {
            "refs/heads/master", "refs/heads/side", "refs/tags/v0"}
        # delta entries: c1 root {a:A, b:A}, c2 {a:M, b:D}, c3 {c:A} = 5
        assert len(entries) == 5, entries
        ops = {(e["path"], e["op"]) for e in entries}
        assert ops == {("a.txt", "A"), ("b.txt", "A"), ("a.txt", "M"),
                       ("b.txt", "D"), ("c.txt", "A")}, ops
        # path_history IS the entry stream: b.txt = A then D
        b_hist = sorted(e["op"] for e in entries if e["path"] == "b.txt")
        assert b_hist == ["A", "D"]
        # state at master tip resolvable: apply chain root->tip deltas
        by_commit = {}
        for e in entries:
            by_commit.setdefault(e["commit"], []).append(e)
        master_tip = hdr["checkpoints"]["refs/heads/master"]
        chain, cur = [], master_tip
        while cur:
            chain.append(cur)
            ps = commits[cur]["parents"]
            cur = ps[0] if ps else None
        state = {}
        for oid in reversed(chain):
            for e in by_commit.get(oid, []):
                if e["op"] == "D":
                    state.pop(e["path"], None)
                else:
                    state[e["path"]] = e["blob"]
        assert set(state) == {"a.txt"}, state  # b deleted, c is side-only
        # incremental: second run adds nothing, file stable in counts
        s2 = run_extract(repo, index)
        assert s2["new"] == 0 and s2["commits"] == 3, s2
        # capped run still checkpoints all refs
        idx2 = os.path.join(d, "idx2.jsonl")
        s3 = run_extract(repo, idx2, "--max-commits", "2")
        assert s3["new"] == 2 and s3["truncated"] is True, s3


if __name__ == "__main__":
    test_extract_incremental_and_derivable()
    print("ok")
