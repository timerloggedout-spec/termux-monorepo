#!/usr/bin/env python3
"""Scrape field-size counts (participants + submitted projects) for the
challenge slate from the platforms' own server-rendered/embedded data —
no headless browser, no API keys (owner order 2026-10-28; field size is
REQUIRED OSINT, see docs/ops/CHALLENGE-SCHEMA.md).

Adapters (verified live 2026-10-28 against the browser-pass values):
- aws-builder-center: the SPA server-renders "<N> participants" in the
  page HTML. Submitted-project totals are NOT in the HTML (loaded via
  api.builder.aws.com) — projects are left untouched by this adapter.
- devpost: the page HTML carries "Participants (<N>)"; the project
  gallery either states it is unpublished (projects = 0) or paginates
  "a – b of <N>".
- lablab-ai: the page embeds JSON `"initialParticipants":<N>` (the
  displayed "Approved <N>" counter).
- builder-io / aha-io: no public count exists on the page (verified) —
  the event stays open_task; the adapter still tries the generic
  patterns so a future count is picked up if one appears.

Writes coordinator events[].field_size{} in place (participants +
source + fetched_at; projects only when the adapter actually sourced
them — a known count is never overwritten with null). Status:
established = participants + projects known; partial = one known;
open_task = none. Run by .github/workflows/challenge-osint-watch.yml
before osint_watch.py. A fetch/parse failure leaves the event's
existing field_size untouched and warns — never fails the watch.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/126 Safari/537.36"}


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", "replace")


def _num(s: str) -> int:
    return int(s.replace(",", ""))


def parse_builder_center(html: str) -> dict:
    m = re.search(r"([\d,]+)\s+participants", html)
    return {"participants": _num(m.group(1)) if m else None}


def parse_devpost(html: str) -> dict:
    m = re.search(r"Participants\s*\(([\d,]+)\)", html)
    return {"participants": _num(m.group(1)) if m else None}


def parse_devpost_gallery(html: str) -> dict:
    if "haven't published" in html or "not published" in html:
        return {"projects": 0, "projects_note": "project gallery unpublished by the organizers"}
    m = re.search(r"\bof\s+([\d,]+)\b", html)
    return {"projects": _num(m.group(1)) if m else None}


def parse_lablab(html: str) -> dict:
    m = re.search(r'"initialParticipants"\s*:\s*(\d+)', html)
    return {"participants": _num(m.group(1)) if m else None}


PARSERS = {
    "aws-builder-center": parse_builder_center,
    "devpost": parse_devpost,
    "lablab-ai": parse_lablab,
}

SOURCES = {
    "aws-builder-center": "event page HTML (server-rendered '<N> participants'), builder.aws.com",
    "devpost": "event page HTML ('Participants (<N>)'), devpost.com",
    "lablab-ai": "event page embedded JSON (initialParticipants = displayed Approved counter), lablab.ai",
}


def scrape_event(ev: dict, fetch=fetch_text) -> dict:
    """Return the field_size update dict for one event ({} = no change)."""
    platform = ev.get("platform")
    url = ev.get("official_url")
    parser = PARSERS.get(platform)
    if not url or (not parser and platform not in ("builder-io", "aha-io")):
        return {}
    try:
        out = parser(fetch(url)) if parser else parse_devpost(fetch(url))
    except Exception as exc:  # never fail the watch on one platform
        print(f"::warning title=field-size::{ev.get('id')} fetch failed: {type(exc).__name__}")
        return {}
    upd: dict = {}
    if out.get("participants") is not None:
        upd["participants"] = out["participants"]
        upd["participants_source"] = SOURCES.get(platform, "event page HTML, participant counter")
    if platform == "devpost":
        try:
            g = parse_devpost_gallery(fetch(url.rstrip("/") + "/project-gallery"))
        except Exception as exc:
            print(f"::warning title=field-size::{ev.get('id')} gallery fetch failed: {type(exc).__name__}")
            g = {}
        if g.get("projects") is not None:
            upd["projects"] = g["projects"]
            upd["projects_source"] = "Devpost project gallery, devpost.com"
            if g.get("projects_note"):
                upd["projects_note"] = g["projects_note"]
    return upd


def apply_update(ev: dict, upd: dict, now: str) -> None:
    fs = dict(ev.get("field_size") or {})
    fs.update(upd)
    fs["fetched_at"] = now
    have_p = fs.get("participants") is not None
    have_j = fs.get("projects") is not None
    fs["status"] = "established" if (have_p and have_j) else ("partial" if (have_p or have_j) else "open_task")
    # An event whose projects count was not sourced by THIS run keeps a
    # prior "partial" (e.g. D1: 1 project so far, event still open) —
    # established requires the projects count to be settled, not growing.
    prior = (ev.get("field_size") or {}).get("status")
    if prior == "partial" and "projects" not in upd and fs["status"] == "established":
        fs["status"] = "partial"
    ev["field_size"] = fs
    mi = ev.get("metrics_internal", {}).get("win_probability")
    if mi is not None:
        mi.setdefault("inputs", {})["participants"] = fs.get("participants")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".")
    ns = ap.parse_args()
    path = Path(ns.root) / "ops/challenge/coordinator.json"
    coord = json.loads(path.read_text())
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    changed = 0
    for ev in coord.get("events", []):
        upd = scrape_event(ev)
        if upd:
            before = json.dumps(ev.get("field_size") or {}, sort_keys=True)
            apply_update(ev, upd, now)
            if json.dumps(ev["field_size"], sort_keys=True) != before:
                changed += 1
                print(f"{ev['id']}: participants={ev['field_size'].get('participants')} "
                      f"projects={ev['field_size'].get('projects')} status={ev['field_size']['status']}")
    if changed:
        path.write_text(json.dumps(coord, indent=2) + "\n")
    print(f"field-size scrape: {changed} event(s) updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
