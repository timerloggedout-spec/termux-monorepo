"""Podium crawler/ingest tests — network-free, fixture-based.

[MUSEai]@{role:{scraping-tools}}
"""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts" / "podium"))

from podium_crawl import parse_edition, parse_prize_tiers, parse_judges, parse_winners_feed
from podium_ingest import normalize, resolve, diff

EDITION_HTML = """
<html><body>
<h1>Acme Hackathon</h1>
<div>🥇 1st place</div><div>$5,000</div><div>+ $3,000 in credits</div>
<div>🥈 2nd place</div><div>$3,000</div><div>+ $1,000 in credits</div>
<h2>Speakers, Mentors &amp; Judges</h2>
<div>Jane Doe</div><div>CEO</div>
<div>John Roe</div><div>Product Manager</div>
<div>Jane Doe</div><div>CEO</div>
<div>Disclosures</div><div>legal text</div>
</body></html>
"""

FEED_HTML = """
<div><a href="/ai-hackathons/acme/team-one/proj-a">
<img alt="Proj A title" src="/x.png"/>
<img src="/_next/image?url=%2Fimg%2Ficons%2F1st_place_icon.png"/>
<span class="inline-flex rounded-full bg-[#e1effe] px-2">Python</span>
</a></div>
<div><a href="/ai-hackathons/acme/team-two/proj-b">
<img alt="Proj B title" src="/y.png"/>
</a></div>
"""


class CrawlTests(unittest.TestCase):
    def test_tiers(self):
        tiers = parse_prize_tiers([
            "🥇 1st place", "$5,000", "+ $3,000 in credits",
            "🥈 2nd place", "$3,000", "+ $1,000 in credits",
            "🥇 1st place", "$5,000", "+ $3,000 in credits",
        ])
        self.assertEqual(len(tiers), 2)
        self.assertEqual(tiers[0]["amounts"], ["$5,000", "$3,000"])

    def test_judges_dedupe(self):
        judges = parse_judges([
            "Speakers, Mentors & Judges", "Jane Doe", "CEO",
            "John Roe", "Product Manager", "Jane Doe", "CEO", "Disclosures",
        ])
        self.assertEqual([j["name"] for j in judges], ["Jane Doe", "John Roe"])

    def test_edition_parse(self):
        out = parse_edition("acme", EDITION_HTML, "2026-11-03T00:00:00Z")
        self.assertEqual(out["edition"]["title"], "Acme Hackathon")
        self.assertEqual(len(out["prize_tiers"]), 2)
        self.assertEqual(len(out["judges"]), 2)
        self.assertEqual(out["edition"]["receipt"]["source_url"],
                         "https://lablab.ai/ai-hackathons/acme")

    def test_winners_feed(self):
        projects = parse_winners_feed(FEED_HTML, "2026-11-03T00:00:00Z")
        self.assertEqual(len(projects), 2)
        self.assertEqual(projects[0]["placement"], "1st")
        self.assertEqual(projects[0]["team_slug"], "team-one")
        self.assertIsNone(projects[1]["placement"])


class IngestTests(unittest.TestCase):
    SNAP = {
        "captured_at": "2026-11-03T00:00:00Z", "collector": "test",
        "editions": [{"slug": "acme", "title": "Acme", "url": "u",
                      "dates_seen": [], "receipt": {"source_url": "s"}}],
        "prize_tiers": [], "judges": [],
        "projects": [{"edition_slug": "acme", "team_slug": "t", "project_slug": "p",
                      "title": "P", "placement": "1st", "url": "u2",
                      "tech_tags": [], "receipt": {"source_url": "s2"}}],
    }

    def test_normalize_and_diff(self):
        ents, conflicts = resolve(normalize(self.SNAP))
        self.assertEqual(conflicts, [])
        self.assertEqual(len(ents), 2)
        d = diff(None, ents)
        self.assertEqual(d["counts"], {"added": 2, "removed": 0, "changed": 0})
        d2 = diff({"version": "v0", "entities": ents}, ents)
        self.assertEqual(d2["counts"], {"added": 0, "removed": 0, "changed": 0})

    def test_conflict_kept(self):
        snap2 = dict(self.SNAP)
        snap2["projects"] = self.SNAP["projects"] + [
            {"edition_slug": "acme", "team_slug": "t", "project_slug": "p",
             "title": "P", "placement": "2nd", "url": "u2",
             "tech_tags": [], "receipt": {"source_url": "s3"}}]
        _, conflicts = resolve(normalize(snap2))
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]["field"], "placement_feed")
        self.assertEqual(sorted(conflicts[0]["values"]), ["1st", "2nd"])


if __name__ == "__main__":
    unittest.main()
