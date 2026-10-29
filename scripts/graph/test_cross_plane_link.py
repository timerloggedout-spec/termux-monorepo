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
CHALLENGE = {
    "updated_at": "2026-10-29T00:00:00Z",
    "events": [{
        "id": "D1", "name": "Workshop to Ship",
        "field_size": {"status": "partial", "participants": 5917, "projects": None,
                       "participants_source": "event page HTML", "fetched_at": "2026-10-28T22:11:14Z"},
        "organizers": [{"name": "AWS Builder Center", "role": "host"}],
        "judges": [{"name": "Jane Judge"}],
        "projects": [{"name": "Our Entry", "url": "https://github.com/owner1/b_fork"}],
        "participants": [{
            "team_name": "Ladder Team",
            "project": {"name": "Ladder: practice sets", "url": "https://example.com/ladder"},
            "persona": {"public_links": {"github": "https://github.com/someone"}},
            "past_wins": [{"event": "Old Hack 2025", "place": 1}],
            "recruitment": {"candidate": True, "pipeline_state": "identified"},
        }],
        "metrics_internal": {"win_probability": 0.003},
    }],
}

class LinkPass(unittest.TestCase):
    def run_build(self, challenge=None):
        d = tempfile.mkdtemp()
        rp = write(d, "r.json", REPO_INDEX); xp = write(d, "x.json", X_INDEX)
        sd = Path(d) / "seeds"; sd.mkdir(); write(sd, "s.json", SEED)
        cp = write(d, "c.json", challenge) if challenge is not None else None
        return build(rp, xp, str(sd), cp)
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
    def test_challenge_import(self):
        edges, summary = self.run_build(challenge=CHALLENGE)
        triples = {(e["src"], e["type"], e["dst"]) for e in edges}
        self.assertIn(("challenge:participant:D1/ladder-team", "competes_in", "challenge:event:D1"), triples)
        self.assertIn(("challenge:participant:D1/ladder-team", "entered_with", "challenge:project:D1/ladder-practice-sets"), triples)
        self.assertIn(("challenge:project:D1/ladder-practice-sets", "submitted_to", "challenge:event:D1"), triples)
        self.assertIn(("challenge:project:D1/our-entry", "hosted_at", "github:repository:owner1/b_fork"), triples)
        self.assertIn(("challenge:participant:D1/ladder-team", "same_author_as", "github:user:someone"), triples)
        self.assertIn(("challenge:participant:D1/ladder-team", "won", "challenge:event:old-hack-2025"), triples)
        self.assertIn(("challenge:judge:jane-judge", "judges", "challenge:event:D1"), triples)
        self.assertIn(("challenge:organizer:aws-builder-center", "organizes", "challenge:event:D1"), triples)
        self.assertEqual(summary["sources"]["challenge"]["tracked_records"]["participants"], 1)
        self.assertNotIn("records", summary["sources"]["challenge"])
    def test_challenge_field_size_carried_as_event_attributes(self):
        edges, summary = self.run_build(challenge=CHALLENGE)
        fs = summary["sources"]["challenge"]["field_size_by_event"]
        # tracked_records (1) and field size (5917) are different quantities
        self.assertEqual(fs["challenge:event:D1"],
                         {"participants": 5917, "projects": None, "status": "partial"})
        # only the three attribute keys are carried — no source notes/fetched_at
        self.assertEqual(set(fs["challenge:event:D1"]), {"participants", "projects", "status"})
    def test_metrics_internal_never_imported(self):
        edges, summary = self.run_build(challenge=CHALLENGE)
        blob = json.dumps(edges) + json.dumps(summary)
        self.assertNotIn("win_probability", blob)
        self.assertNotIn("metrics_internal", blob)

if __name__ == "__main__":
    unittest.main()
