from __future__ import annotations

import datetime as dt
import json
import tempfile
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from render_github_profile import parse_partners, parse_videos, render, select_spotlight, safe_offer


class GitHubProfileRendererTests(unittest.TestCase):
    def test_partner_parser_reads_active_rows_and_keeps_source_urls(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "PARTNERS.md"
            path.write_text(
                "## 1. Active lanes (tracked link live)\n"
                "| Partner | Category | Offer | Link | Badge | Owner |\n"
                "|---|---|---|---|---|---|\n"
                "| Alpha | AI tools | 10 credits | https://alpha.example/ref | badge | owner |\n"
                "## 1b. Code lanes\n",
                encoding="utf-8",
            )
            rows = parse_partners(path)
            self.assertEqual(rows[0]["name"], "Alpha")
            self.assertEqual(rows[0]["url"], "https://alpha.example/ref")

    def test_unverified_offer_is_suppressed(self):
        self.assertEqual(safe_offer("500 credits (verify on signup)"), "")
        self.assertEqual(safe_offer("10% referral credit"), "10% referral credit")

    def test_weekly_spotlight_is_deterministic_and_advances(self):
        partners = [{"name": "A"}, {"name": "B"}, {"name": "C"}]
        monday = dt.date(2026, 11, 16)
        self.assertEqual(select_spotlight(partners, monday), select_spotlight(partners, monday))
        self.assertNotEqual(select_spotlight(partners, monday), select_spotlight(partners, monday + dt.timedelta(days=7)))

    def test_video_parser_extracts_short_and_watch_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "videos.md"
            path.write_text(
                "## Curated public assets\n"
                "| Group | Video | Duration | Published | Purpose |\n"
                "|---|---|---:|---|---|\n"
                "| Latest | [A Short](https://youtube.com/shorts/abc123) | 0:08 | 2026-11-14 | Update |\n"
                "| Demo | [A Demo](https://www.youtube.com/watch?v=xyz789) | 1:00 | 2026-11-01 | Demo |\n"
                "## Public placements\n",
                encoding="utf-8",
            )
            rows = parse_videos(path)
            self.assertIn("abc123", rows)
            self.assertIn("xyz789", rows)

    def test_render_creates_readme_and_three_svg_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "marketing/github-profile").mkdir(parents=True)
            (root / "docs/ops").mkdir(parents=True)
            (root / "docs").mkdir(exist_ok=True)
            (root / "docs/PARTNERS.md").write_text(
                "## 1. Active lanes\n"
                "| Partner | Category | Offer | Link | Badge | Owner |\n"
                "|---|---|---|---|---|---|\n"
                "| Alpha | AI tools | 10 credits | https://alpha.example/ref | badge | owner |\n"
                "## 1b. Code lanes\n",
                encoding="utf-8",
            )
            (root / "docs/ops/PUBLIC-VIDEO-LIBRARY-2026-11-15.md").write_text(
                "## Curated public assets\n"
                "| Group | Video | Duration | Published | Purpose |\n"
                "|---|---|---:|---|---|\n"
                "| Latest | [A Short](https://youtube.com/shorts/abc123) | 0:08 | 2026-11-14 | Update |\n"
                "## Public placements\n",
                encoding="utf-8",
            )
            config = {
                "identity": {
                    "handle": "timerloggedout-spec",
                    "headline": "Built in the open",
                    "summary": "Evidence-backed work",
                    "website": "https://example.com/",
                    "monorepo": "https://github.com/example/repo",
                    "youtube_channel": "https://youtube.com/@example",
                    "video_library": "https://example.com/videos"
                },
                "sources": {"partners": "docs/PARTNERS.md", "videos": "docs/ops/PUBLIC-VIDEO-LIBRARY-2026-11-15.md"},
                "featured_projects": [{"name": "Repo", "url": "https://github.com/example/repo", "description": "Project"}],
                "featured_videos": [{"id": "abc123", "label": "Latest Short", "kind": "short"}],
                "rotation": {"disclosure": "Referral links may be affiliate links."}
            }
            (root / "marketing/github-profile/profile.json").write_text(json.dumps(config), encoding="utf-8")
            output = root / "out"
            result = render(root, output, dt.date(2026, 11, 16))
            self.assertEqual(result["partner"], "Alpha")
            self.assertTrue((output / "README.md").exists())
            self.assertTrue((output / "assets/hero.svg").exists())
            self.assertTrue((output / "assets/highlights.svg").exists())
            self.assertTrue((output / "assets/partner-spotlight.svg").exists())
            generated_readme = (output / "README.md").read_text(encoding="utf-8")
            self.assertIn("Referral links may be affiliate links.", generated_readme)
            self.assertIn("Hackathon highlight", generated_readme)


    def _write_fixture(self, root, video_rows, featured_videos):
        (root / "marketing/github-profile").mkdir(parents=True)
        (root / "docs/ops").mkdir(parents=True)
        (root / "docs/PARTNERS.md").write_text(
            "## 1. Active lanes\\n"
            "| Partner | Category | Offer | Link | Badge | Owner |\\n"
            "|---|---|---|---|---|---|\\n"
            "| Alpha | AI tools | 10 credits | https://alpha.example/ref | badge | owner |\\n"
            "## 1b. Code lanes\\n",
            encoding="utf-8",
        )
        video_text = (
            "## Curated public assets\\n"
            "| Group | Video | Duration | Published | Purpose |\\n"
            "|---|---|---:|---|---|\\n"
            + "".join(video_rows)
            + "## Public placements\\n"
        )
        (root / "docs/ops/PUBLIC-VIDEO-LIBRARY-2026-11-15.md").write_text(video_text, encoding="utf-8")
        config = {
            "identity": {
                "handle": "timerloggedout-spec",
                "headline": "Built in the open",
                "summary": "Evidence-backed work",
                "website": "https://example.com/",
                "monorepo": "https://github.com/example/repo",
                "youtube_channel": "https://youtube.com/@example",
                "video_library": "https://example.com/videos"
            },
            "sources": {"partners": "docs/PARTNERS.md", "videos": "docs/ops/PUBLIC-VIDEO-LIBRARY-2026-11-15.md"},
            "featured_projects": [{"name": "Repo", "url": "https://github.com/example/repo", "description": "Project"}],
            "featured_videos": featured_videos,
            "rotation": {"disclosure": "Referral links may be affiliate links."}
        }
        (root / "marketing/github-profile/profile.json").write_text(json.dumps(config), encoding="utf-8")

    def test_latest_short_resolves_current_latest_row_when_previous_short_remains(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_fixture(
                root,
                [
                    "| Latest | [Current Short](https://youtube.com/shorts/current123) | 0:08 | 2026-11-15 | Current update |\\n",
                    "| Archive | [Previous Short](https://youtube.com/shorts/previous123) | 0:08 | 2026-11-14 | Prior update |\\n",
                ],
                [{"source": "latest", "label": "Latest Short", "kind": "short"}],
            )
            output = root / "out"
            try:
                render(root, output, dt.date(2026, 11, 16))
            except (KeyError, ValueError) as exc:
                self.fail(f"renderer must resolve the Latest slot from the current library row: {type(exc).__name__}: {exc}")
            generated = (output / "README.md").read_text(encoding="utf-8")
            self.assertIn("https://youtube.com/shorts/current123", generated)
            self.assertNotIn("previous123", generated)

    def test_hackathon_highlight_renders_submission_summary_and_build_story(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_fixture(
                root,
                [
                    "| Archive | [StudySprint v0.4.0 demo](https://www.youtube.com/watch?v=WK9LMwpvHUk) | 2:55 | 2026-11-03 | Earlier release |\\n",
                ],
                [{
                    "id": "WK9LMwpvHUk",
                    "label": "StudySprint hackathon submission",
                    "kind": "hackathon",
                    "highlight": "Official AWS Builder Center D1 submission demo.",
                    "related_url": "https://builder.aws.com/project/example/studysprint"
                }],
            )
            output = root / "out"
            render(root, output, dt.date(2026, 11, 16))
            generated = (output / "README.md").read_text(encoding="utf-8")
            self.assertIn("Official AWS Builder Center D1 submission demo.", generated)
            self.assertIn("[Build story](https://builder.aws.com/project/example/studysprint)", generated)

    def test_weekly_spotlight_advances_one_partner_across_iso_year_boundaries(self):
        partners = [{"name": "A"}, {"name": "B"}, {"name": "C"}, {"name": "D"}]
        for monday in (dt.date(2026, 12, 28), dt.date(2027, 12, 27)):
            following_monday = monday + dt.timedelta(days=7)
            current = select_spotlight(partners, monday)
            following = select_spotlight(partners, following_monday)
            expected = partners[(partners.index(current) + 1) % len(partners)]
            self.assertEqual(following, expected, f"rotation must advance one slot from {monday} to {following_monday}")


if __name__ == "__main__":
    unittest.main()
