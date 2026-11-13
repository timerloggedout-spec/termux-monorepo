#!/usr/bin/env python3
"""Validate the agent-readable static surfaces before Pages publication."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGES = [
    ("apps/tribute-dashboard/index.html", "apps/tribute-dashboard/index.md",
     "https://timerloggedout-spec.github.io/tribute/", "/tribute/index.md"),
    ("apps/tribute-dashboard/matrix.html", "apps/tribute-dashboard/matrix.md",
     "https://timerloggedout-spec.github.io/matrix/", "/matrix/index.md"),
    ("apps/project-pages-hub/index.html", "apps/project-pages-hub/index.md",
     "https://timerloggedout-spec.github.io/termux-monorepo/", "/termux-monorepo/index.md"),
]
errors: list[str] = []

def require(ok: bool, message: str) -> None:
    if not ok:
        errors.append(message)

for html_path, md_path, canonical, alternate in PAGES:
    html_file = ROOT / html_path
    md_file = ROOT / md_path
    require(html_file.is_file(), f"missing HTML source: {html_path}")
    require(md_file.is_file(), f"missing Markdown mirror: {md_path}")
    if not html_file.is_file() or not md_file.is_file():
        continue
    html = html_file.read_text(encoding="utf-8")
    markdown = md_file.read_text(encoding="utf-8")

    hidden_controls = re.compile(r"[\\u200b\\u200e\\u200f\\u202a-\\u202e\\u2060\\ufeff]")
    require(hidden_controls.search(html) is None, f"{html_path}: hidden or bidirectional control character found in public HTML")
    require(hidden_controls.search(markdown) is None, f"{md_path}: hidden or bidirectional control character found in public Markdown")

    require(f'<link rel="canonical" href="{canonical}">' in html, f"{html_path}: canonical missing")
    require(bool(re.search(r'<meta name="description" content="[^"]{50,}"', html)), f"{html_path}: useful meta description missing")
    require('property="og:title"' in html, f"{html_path}: Open Graph title missing")
    require(bool(re.search(r'<meta property="og:description" content="[^"]{50,}"', html)), f"{html_path}: P8 requires a populated Open Graph description of at least 50 characters")
    require('name="robots" content="index, follow, max-snippet:-1, max-image-preview:large"' in html, f"{html_path}: AI snippet directives missing")
    require(f'<link rel="alternate" type="text/markdown" href="{alternate}">' in html, f"{html_path}: Markdown alternate missing")
    require('<link rel="describedby" href="/llms.txt">' in html, f"{html_path}: llms.txt discovery missing")
    require("/glossary.md" in html, f"{html_path}: glossary link missing")
    require("<main" in html and "</main>" in html, f"{html_path}: main landmark missing")
    require("Skip to main content" in html, f"{html_path}: skip link missing")
    if html_path == "apps/tribute-dashboard/index.html":
        require("Evidence and freshness" in html, "Tribute page needs a static evidence/freshness explanation")

    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    require(bool(blocks), f"{html_path}: JSON-LD missing")
    for block in blocks:
        try:
            data = json.loads(block)
        except json.JSONDecodeError as exc:
            errors.append(f"{html_path}: invalid JSON-LD: {exc}")
            continue
        for key in ("@type", "name", "headline", "description", "url", "dateModified"):
            require(bool(data.get(key)), f"{html_path}: JSON-LD missing {key}")

    require(markdown.startswith("---\n"), f"{md_path}: YAML frontmatter missing")
    frontmatter = markdown.split("---", 2)[1] if markdown.startswith("---\n") else ""
    for field in ("title:", "description:", "last_updated:"):
        require(field in frontmatter, f"{md_path}: frontmatter missing {field}")
    require(bool(re.search(r"(?m)^# ", markdown)), f"{md_path}: H1 missing")
    require(bool(re.search(r"(?m)^## Sitemap\s*$", markdown)), f"{md_path}: Sitemap section missing")

    headings = re.findall(r"<h[1-6][^>]*>(.*?)</h[1-6]>", html, re.S | re.I)
    heading_text = [re.sub(r"<[^>]+>", "", value).strip() for value in headings]
    require(len(heading_text) >= 3, f"{html_path}: fewer than three headings")
    require(all(heading_text), f"{html_path}: empty heading found")

hub = (ROOT / "apps/project-pages-hub/index.html").read_text(encoding="utf-8")
require(not re.search(r'<meta[^>]+http-equiv=["\']refresh', hub, re.I), "project hub must not auto-redirect away from its navigation content")

workflow = (ROOT / ".github/workflows/tribute-dashboard-deploy.yml").read_text(encoding="utf-8")
for statement in (
    "cp apps/project-pages-hub/index.md _site/index.md",
    "cp apps/tribute-dashboard/matrix.md _site/matrix.md",
    "cp apps/tribute-dashboard/matrix.md _user_site/matrix/index.md",
    "main-landing-studysprint-link",
    "force:false",
    "cp -a _tribute/. _user_site/tribute/",
):
    require(statement in workflow, f"Pages deployment does not publish mirror: {statement}")

if errors:
    print("Agent readability source contract: FAIL")
    for error in errors:
        print(f" - {error}")
    sys.exit(1)

print("Agent readability source contract: PASS (Tribute, Matrix, project hub; HTML/Markdown parity and deployment copies)")
