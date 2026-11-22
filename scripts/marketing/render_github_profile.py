#!/usr/bin/env python3
"""Render the GitHub profile projection from Termux MonoRepo source records.

The partner registry and public video library remain the canonical content sources.
This renderer produces a reviewable README plus static SVG display assets.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import urllib.parse
from pathlib import Path


def table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def parse_partners(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    if "## 1. Active lanes" not in text or "## 1b." not in text:
        raise ValueError("docs/PARTNERS.md active-lanes section is missing")
    section = text.split("## 1. Active lanes", 1)[1].split("## 1b.", 1)[0]
    rows: list[dict[str, str]] = []
    for line in section.splitlines():
        if not line.startswith("|"):
            continue
        cells = table_cells(line)
        if not cells or cells[0] in {"Partner", "---"} or len(cells) < 6:
            continue
        name, category, offer, url, _badge, _owner = cells[:6]
        if not name or not url.startswith("https://"):
            continue
        rows.append({"name": name, "category": category, "offer": offer, "url": url})
    if not rows:
        raise ValueError("No active partner rows were parsed from docs/PARTNERS.md")
    return rows


def video_id_from_url(url: str) -> str | None:
    parsed = urllib.parse.urlparse(url)
    host = parsed.netloc.lower()
    if host.endswith("youtu.be"):
        return parsed.path.strip("/").split("/")[0] or None
    if "youtube.com" not in host:
        return None
    if parsed.path.startswith("/shorts/"):
        return parsed.path.split("/")[2] if len(parsed.path.split("/")) > 2 else None
    if parsed.path == "/watch":
        return urllib.parse.parse_qs(parsed.query).get("v", [None])[0]
    return None


def parse_videos(path: Path) -> dict[str, dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    if "## Curated public assets" not in text or "## Public placements" not in text:
        raise ValueError("Public video library table is missing")
    section = text.split("## Curated public assets", 1)[1].split("## Public placements", 1)[0]
    videos: dict[str, dict[str, str]] = {}
    for line in section.splitlines():
        if not line.startswith("|"):
            continue
        cells = table_cells(line)
        if not cells or cells[0] in {"Group", "---"} or len(cells) < 5:
            continue
        group, linked_title, duration, published, purpose = cells[:5]
        match = re.search(r"\[([^\]]+)\]\((https?://[^)]+)\)", linked_title)
        if not match:
            continue
        title, url = match.groups()
        video_id = video_id_from_url(url)
        if video_id:
            videos[video_id] = {
                "group": group, "title": title, "url": url,
                "duration": duration, "published": published, "purpose": purpose
            }
    if not videos:
        raise ValueError("No YouTube videos were parsed from the public video library")
    return videos


def select_spotlight(partners: list[dict[str, str]], date: dt.date) -> dict[str, str]:
    year, week, _weekday = date.isocalendar()
    index = ((year * 53) + week) % len(partners)
    return partners[index]


def safe_offer(offer: str) -> str:
    lowered = offer.lower()
    if any(term in lowered for term in ("not established", "unverified", "verify on signup", "verify before")):
        return ""
    return offer.strip()


def make_hero_svg(config: dict) -> str:
    identity = config["identity"]
    headline = html.escape(identity["headline"])
    summary = html.escape(identity["summary"])
    handle = html.escape(identity["handle"])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="360" viewBox="0 0 1200 360" role="img" aria-labelledby="title desc">
<title id="title">{headline}</title>
<desc id="desc">{summary}</desc>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#081522"/><stop offset="1" stop-color="#172b42"/></linearGradient>
  <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#50e3c2"/><stop offset="1" stop-color="#6aa8ff"/></linearGradient>
  <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="#7ba3c9" stroke-opacity=".12"/></pattern>
</defs>
<rect width="1200" height="360" rx="28" fill="url(#bg)"/>
<rect width="1200" height="360" rx="28" fill="url(#grid)"/>
<circle cx="1030" cy="80" r="155" fill="#50e3c2" opacity=".08"/>
<circle cx="1100" cy="290" r="190" fill="#6aa8ff" opacity=".08"/>
<path d="M790 280L930 135L1080 220" fill="none" stroke="url(#accent)" stroke-width="3" opacity=".8"/>
<g fill="#50e3c2"><circle cx="790" cy="280" r="7"/><circle cx="930" cy="135" r="7"/><circle cx="1080" cy="220" r="7"/></g>
<text x="76" y="82" fill="#83a9c8" font-family="monospace" font-size="19" letter-spacing="4">{handle}</text>
<text x="76" y="166" fill="#f4f8fc" font-family="Arial,sans-serif" font-size="43" font-weight="700">{headline}</text>
<text x="76" y="220" fill="#b8c9d9" font-family="Arial,sans-serif" font-size="22">{summary}</text>
<rect x="76" y="274" width="370" height="5" rx="2.5" fill="url(#accent)"/>
<text x="76" y="318" fill="#83a9c8" font-family="monospace" font-size="15" letter-spacing="3">BUILD · DEMO · EVIDENCE · REPEAT</text>
</svg>
'''


def make_spotlight_svg(partner: dict[str, str], week_label: str) -> str:
    name = html.escape(partner["name"])
    category = html.escape(partner["category"])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="180" viewBox="0 0 900 180" role="img" aria-labelledby="title">
<title id="title">Featured partner: {name}</title>
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#103b43"/><stop offset="1" stop-color="#17304c"/></linearGradient></defs>
<rect width="900" height="180" rx="20" fill="url(#g)"/>
<text x="34" y="48" fill="#8ce8d5" font-family="monospace" font-size="16" letter-spacing="3">FEATURED PARTNER · {html.escape(week_label)}</text>
<text x="34" y="104" fill="#ffffff" font-family="Arial,sans-serif" font-size="34" font-weight="700">{name}</text>
<text x="34" y="142" fill="#c5d5e3" font-family="Arial,sans-serif" font-size="18">{category}</text>
<circle cx="824" cy="90" r="38" fill="#50e3c2" opacity=".15"/>
<path d="M808 90h32m-12 -12 12 12 -12 12" fill="none" stroke="#8ce8d5" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
'''


def make_highlights_svg(videos: list[dict[str, str]]) -> str:
    labels = "  ·  ".join(html.escape(item["label"]) for item in videos[:3])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="130" viewBox="0 0 900 130" role="img" aria-labelledby="title">
<title id="title">Video highlights</title>
<rect width="900" height="130" rx="18" fill="#111d2b"/>
<text x="30" y="46" fill="#7ea9cb" font-family="monospace" font-size="15" letter-spacing="3">WATCH THE BUILDS</text>
<text x="30" y="88" fill="#f3f7fb" font-family="Arial,sans-serif" font-size="22">{labels}</text>
</svg>
'''


def render(root: Path, output: Path, as_of: dt.date | None = None) -> dict[str, str]:
    config_path = root / "marketing/github-profile/profile.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    partners = parse_partners(root / config["sources"]["partners"])
    videos = parse_videos(root / config["sources"]["videos"])
    featured = []
    for spec in config["featured_videos"]:
        video = videos.get(spec["id"])
        if video is None:
            raise ValueError(f"Featured video {spec['id']} is absent from the canonical library")
        featured.append({**video, **spec})
    date = as_of or dt.datetime.now(dt.timezone.utc).date()
    partner = select_spotlight(partners, date)
    week_label = f"{date.isocalendar().year}-W{date.isocalendar().week:02d}"
    output.mkdir(parents=True, exist_ok=True)
    assets = output / "assets"
    assets.mkdir(parents=True, exist_ok=True)

    identity = config["identity"]
    project_rows = "\n".join(
        f"- **[{html.escape(p['name'])}]({p['url']})** — {html.escape(p['description'])}"
        for p in config["featured_projects"]
    )
    video_rows = []
    for item in featured:
        thumbnail = f"https://i.ytimg.com/vi/{item['id']}/hqdefault.jpg"
        video_rows.append(
            f'<a href="{item["url"]}"><img src="{thumbnail}" width="220" alt="{html.escape(item["title"])}"></a>\n'
            f'**[{html.escape(item["label"])}]({item["url"]})** · {html.escape(item["title"])}'
        )
    offer = safe_offer(partner["offer"])
    offer_line = f"\n\n{html.escape(offer)}" if offer else ""
    readme = f'''<p align="center"><img src="./assets/hero.svg" alt="Software built in the open with receipts" width="100%"></p>

<p align="center">
  <a href="{identity["website"]}">Website</a> ·
  <a href="{identity["monorepo"]}">Termux MonoRepo</a> ·
  <a href="{identity["youtube_channel"]}">YouTube</a> ·
  <a href="{identity["video_library"]}">Video library</a>
</p>

## Featured work

{project_rows}

## Watch the work

<p align="center"><img src="./assets/highlights.svg" alt="Video highlights" width="100%"></p>

{chr(10).join(video_rows)}

### Hackathon highlight

{next((f"**[{v['title']}]({v['url']})** — {html.escape(v['purpose'])}" for v in featured if v["kind"] == "hackathon"), "See the public video library for current demos.")}

## Partner spotlight · {week_label}

<p align="center"><img src="./assets/partner-spotlight.svg" alt="Featured partner spotlight" width="100%"></p>

**[{html.escape(partner["name"])}]({partner["url"]})** · {html.escape(partner["category"])}{offer_line}

[Browse all active partner links](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/PARTNERS.md).

{config["rotation"]["disclosure"]}

---

<p align="center">BUILD · DEMO · EVIDENCE · REPEAT</p>
'''
    (output / "README.md").write_text(readme, encoding="utf-8")
    (assets / "hero.svg").write_text(make_hero_svg(config), encoding="utf-8")
    (assets / "partner-spotlight.svg").write_text(make_spotlight_svg(partner, week_label), encoding="utf-8")
    (assets / "highlights.svg").write_text(make_highlights_svg(featured), encoding="utf-8")
    return {"partner": partner["name"], "week": week_label, "videos": str(len(featured)), "output": str(output)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--date", type=dt.date.fromisoformat, default=None)
    args = parser.parse_args()
    output = args.output or args.root / "marketing/github-profile/generated"
    result = render(args.root.resolve(), output.resolve(), args.date)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
