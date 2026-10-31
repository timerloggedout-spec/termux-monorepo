#!/usr/bin/env python3
"""Build a version-stamped, comparable Help-Wanted dashboard artifact."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ID_OVERRIDES = {
    "index.html": "help-wanted-home",
    "versioning.html": "version-comparison",
}
TITLE_OVERRIDES = {
    "index.html": "Help-Wanted Home",
    "versioning.html": "Version Comparison",
    "3l0.html": "3L0",
    "ates.html": "ATES",
    "doe.html": "DoE",
    "delphi-rfp.html": "Delphi RFP",
    "delphi-ledger.html": "Delphi Ledger",
    "mvt.html": "MVT",
    "pr-lanes.html": "PR Lanes",
}


def page_title(filename: str) -> str:
    return TITLE_OVERRIDES.get(filename, Path(filename).stem.replace("-", " ").replace("_", " ").title())
EXCLUDED = {"sitemap.xml"}


def page_id(filename: str) -> str:
    if filename in ID_OVERRIDES:
        return ID_OVERRIDES[filename]
    return re.sub(r"[^a-z0-9]+", "-", Path(filename).stem.lower()).strip("-")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(root: Path, channel: str, source_ref: str, source_sha: str, version_prefix: str) -> dict:
    root = root.resolve()
    pages = sorted(p for p in root.glob("*.html") if p.is_file())
    if not pages:
        raise ValueError(f"{root}: no HTML pages found; refusing to emit an empty manifest")
    ids = [page_id(page.name) for page in pages]
    if len(ids) != len(set(ids)):
        duplicates = sorted({page_id(name) for name in [p.name for p in pages] if ids.count(page_id(name)) > 1})
        raise ValueError(f"duplicate page unique IDs: {duplicates}")
    for page in pages:
        html = page.read_text(encoding="utf-8")
        if 'src="./versioning.js"' not in html:
            if "</head>" not in html.lower():
                raise ValueError(f"{page.name}: missing </head>; cannot inject version header")
            html = re.sub(r"</head>", ' <script src="./versioning.js" defer></script>\n</head>', html, count=1, flags=re.I)
            page.write_text(html, encoding="utf-8")
    short_sha = source_sha[:12] if source_sha else "unverified"
    manifest = {
        "schema_version": 1,
        "version": f"{version_prefix}+{short_sha}",
        "channel": channel,
        "source_ref": source_ref,
        "source_sha": source_sha,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "comparison": {
            "production_manifest": "https://timerloggedout-spec.github.io/help-wanted/version-manifest.json",
            "repository": "https://github.com/timerloggedout-spec/termux-monorepo",
        },
        "pages": [],
    }
    for page in pages:
        manifest["pages"].append({
            "id": page_id(page.name),
            "file": page.name,
            "title": page_title(page.name),
            "content_sha256": sha256(page),
        })
    (root / "version-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--channel", choices=("production", "preview", "development"), required=True)
    parser.add_argument("--source-ref", required=True)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--version-prefix", default="1.0.1")
    args = parser.parse_args()
    manifest = build(args.root, args.channel, args.source_ref, args.source_sha, args.version_prefix)
    print(json.dumps({"version": manifest["version"], "channel": manifest["channel"], "pages": len(manifest["pages"]), "source_sha": manifest["source_sha"]}))


if __name__ == "__main__":
    main()
