import json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from cross_plane_link import build

def write(d, name, payload):
    p = Path(d) / name; p.write_text(json.dumps(payload)); return str(p)

REPO_INDEX = {
    "observed_at": "2026-10-29T00:00:00Z", "authenticated_user": "owner1",
    "snapshot_hash": "a" * 64,
    "repositories": [
        {"id": "github:repository:a/b", "full_name": "a/b", "owner": "a",
         "provenance": ["starred", "watching"], "topics": ["mcp"],
         "classification": {"domains": ["agent"]}, "upstream": None},
        {"id": "github:repository:owner1/b_fork", "full_name": "owner1/b_fork",
         "owner": "owner1", "provenance": ["owned"], "topics": [],
         "classification": {"domains": []}, "upstream": "a/b"},
    ],
    "issue_intake": [{"seed_id": "github:research-seed:a/b", "upstream": "a/b"}],
}
X_INDEX = {
    "observed_at": "2026-10-29T00:00:00Z", "snapshot_hash": "b" * 64,
    "account": {"username": "ownx"}, "status": "ok",
    "records": [{"id": "x:tweet:1", "tweet_id": "1", "author_handle": "someone",
                 "signals": ["like"], "text_excerpt": "see https://github.com/a/b now"}],
}
SEED = {"seed_id": "github:research-seed:a/b", "canonical_upstream": "a/b",
        "local_fork": "owner1/b_fork", "classification": {"domains": ["platform"]}}

class LinkPass(unittest.TestCase):
    def run_build(self):
        d = tempfile.mkdtemp()
        rp = write(d, "r.json", REPO_INDEX); xp = write(d, "x.json", X_INDEX)
        sd = Path(d) / "seeds"; sd.mkdir(); write(sd, "s.json", SEED)
        return build(rp, xp, str(sd))
    def test_edge_types(self):
        edges, summary = self.run_build()
        triples = {(e["src"], e["type"], e["dst"]) for e in edges}
        self.assertIn(("github:repository:a/b", "authored_by", "github:user:a"), triples)
        self.assertIn(("github:user:owner1", "starred", "github:repository:a/b"), triples)
        self.assertIn(("github:user:owner1", "watching", "github:repository:a/b"), triples)
        self.assertIn(("github:user:owner1", "owned", "github:repository:owner1/b_fork"), triples)
        self.assertIn(("github:repository:owner1/b_fork", "fork_of", "github:repository:a/b"), triples)
        self.assertIn(("github:repository:a/b", "about_topic", "topic:mcp"), triples)
        self.assertIn(("github:repository:a/b", "in_domain", "domain:agent"), triples)
        self.assertIn(("x:tweet:1", "authored_by", "x:user:someone"), triples)
        self.assertIn(("x:user:ownx", "liked", "x:tweet:1"), triples)
        self.assertIn(("x:tweet:1", "mentions_repo", "github:repository:a/b"), triples)
        self.assertIn(("github:research-seed:a/b", "upstream", "github:repository:a/b"), triples)
        self.assertIn(("github:research-seed:a/b", "in_domain", "domain:platform"), triples)
    def test_deterministic_and_deduped(self):
        e1, s1 = self.run_build(); e2, s2 = self.run_build()
        self.assertEqual(e1, e2); self.assertEqual(s1["snapshot_hash"], s2["snapshot_hash"])
        keys = [(e["src"], e["dst"], e["type"]) for e in e1]
        self.assertEqual(len(keys), len(set(keys)))
    def test_x_actor_skipped_when_account_unknown(self):
        d = tempfile.mkdtemp()
        rp = write(d, "r.json", REPO_INDEX)
        xi = dict(X_INDEX); xi["account"] = None
        xp = write(d, "x.json", xi)
        edges, summary = build(rp, xp, None)
        self.assertEqual(summary["counts"]["x_actor_edges_skipped_account_unknown"], 1)

if __name__ == "__main__":
    unittest.main()
