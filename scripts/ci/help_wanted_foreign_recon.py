#!/usr/bin/env python3
"""Foreign-repo recon for help-wanted: CONTRIBUTING.md + comment URL extraction.

Used by followup (and optionally contribute/scout) so each foreign PR adapts to
local maintainer docs and linked notes — not a static template.
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Any

URL_RE = re.compile(r"https?://[^\s)\]\"'<>]+")
CONTRIB_CANDIDATES = (
    "CONTRIBUTING.md",
    "CONTRIBUTING.rst",
    "CONTRIBUTING",
    "docs/CONTRIBUTING.md",
    ".github/CONTRIBUTING.md",
    "CONTRIBUTE.md",
)


def _headers() -> dict[str, str]:
    h = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "termux-help-wanted-foreign-recon",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    tok = (
        os.environ.get("OPERATOR_GITHUB_TOKEN")
        or os.environ.get("OPERATOR_TOKEN")
        or os.environ.get("ARCHWIZ_GITHUB_TOKEN")
        or os.environ.get("GITHUB_TOKEN")
        or os.environ.get("GH_TOKEN")
        or ""
    )
    if tok:
        h["Authorization"] = f"Bearer {tok}"
    return h


def api_get(path: str) -> Any:
    url = path if path.startswith("http") else f"https://api.github.com{path}"
    req = urllib.request.Request(url, headers=_headers())
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            raw = r.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def fetch_contributing(owner: str, repo: str) -> dict[str, Any] | None:
    """Return first found CONTRIBUTING-like doc (path + excerpt)."""
    for path in CONTRIB_CANDIDATES:
        data = api_get(f"/repos/{owner}/{repo}/contents/{path}")
        if not isinstance(data, dict) or data.get("type") != "file":
            continue
        # Prefer download_url to avoid base64 decode complexity on large files
        download = data.get("download_url")
        text = ""
        if download:
            req = urllib.request.Request(download, headers={"User-Agent": "termux-hw-recon"})
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    text = r.read().decode(errors="replace")
            except Exception:
                continue
        if not text.strip():
            continue
        # Keep first ~40 non-empty lines for follow-up context
        lines = [ln for ln in text.splitlines() if ln.strip()][:40]
        excerpt = "\n".join(lines)
        if len(excerpt) > 1800:
            excerpt = excerpt[:1800] + "…"
        return {
            "path": path,
            "html_url": data.get("html_url"),
            "excerpt": excerpt,
            "urls": sorted(set(URL_RE.findall(text)))[:15],
        }
    return None


def extract_urls(*texts: str) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for t in texts:
        for u in URL_RE.findall(t or ""):
            u = u.rstrip(".),;]")
            if u not in seen:
                seen.add(u)
                found.append(u)
    return found[:20]


def format_recon_block(contrib: dict[str, Any] | None, urls: list[str]) -> str:
    parts: list[str] = []
    if contrib:
        parts.append(
            f"**Foreign CONTRIBUTING** (`{contrib.get('path')}`): "
            f"{contrib.get('html_url') or ''}\n"
        )
        # Bullet key imperative lines
        keys = []
        for ln in (contrib.get("excerpt") or "").splitlines():
            s = ln.strip()
            if s.startswith(("-", "*", "1.", "2.", "3.")) or any(
                k in s.lower()
                for k in ("test", "lint", "pr", "fork", "branch", "doc", "style")
            ):
                keys.append(s[:120])
            if len(keys) >= 8:
                break
        if keys:
            parts.append("Key notes:\n" + "\n".join(f"- {k}" for k in keys) + "\n")
    if urls:
        parts.append("**Linked from thread/docs:**\n" + "\n".join(f"- {u}" for u in urls[:12]) + "\n")
    return "\n".join(parts).strip()
