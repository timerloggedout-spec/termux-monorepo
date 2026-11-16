#!/usr/bin/env python3
"""Harvest the DeepWiki.com wiki structure for this repo into the ICM import record.

Source surface: DeepWiki.com public MCP (https://mcp.deepwiki.com/mcp) —
read-only, no credential. This is NOT DEVINdeepWiki (a distinct surface);
nothing from that surface is read or written here.

Behavior (owner order 2026-11-01, ICM run#10 build+automate):
- Calls read_wiki_structure for the repo (in-automation preflight).
- If the repo is not indexed, appends a dated `not_indexed` section to the
  import record and exits 0 — it never fabricates a structure.
- If indexed and the topic set differs from the latest harvest section,
  appends a new dated harvest section (additive only; prior sections kept).
- If unchanged, leaves the record untouched.

The import record is docs/icm/_meta/deepwiki-import-record.md; imported
material is evidence_class generated-external (generated wiki over an index
snapshot, not HEAD).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

MCP_URL = "https://mcp.deepwiki.com/mcp"
DEFAULT_REPO = "timerloggedout-spec/termux-monorepo"
DEFAULT_RECORD = "docs/icm/_meta/deepwiki-import-record.md"


def mcp_post(payload: dict) -> dict:
    req = urllib.request.Request(
        MCP_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = resp.read().decode("utf-8")
    for line in body.splitlines():
        if line.startswith("data: "):
            return json.loads(line[6:])
    if body.strip().startswith("{"):
        return json.loads(body)
    raise ValueError("no JSON-RPC data line in MCP response")


def fetch_structure(repo: str) -> str | None:
    """Return the structure text, or None when the repo is not indexed."""
    mcp_post(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "icm-deepwiki-harvest", "version": "1.0"},
            },
        }
    )
    result = mcp_post(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "read_wiki_structure",
                "arguments": {"repoName": repo},
            },
        }
    )
    if "error" in result:
        return None
    content = result.get("result", {}).get("content", [])
    text = "\n".join(c.get("text", "") for c in content if c.get("type") == "text")
    if "Available pages for" not in text:
        return None
    return text


def parse_structure(text: str) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for line in text.splitlines():
        m = re.match(r"^- ([\d.]+) (.+)$", line)
        if m:
            rows.append((m.group(1), m.group(2), "topic"))
            continue
        m = re.match(r"^  - ([\d.]+) (.+)$", line)
        if m:
            rows.append((m.group(1), m.group(2), "subpage"))
    return rows


def latest_section_rows(record_text: str) -> list[tuple[str, str, str]] | None:
    """Rows of the most recent harvest section, or None if there is none."""
    sections = record_text.split("\n## Harvest — ")
    if len(sections) < 2:
        return None
    rows: list[tuple[str, str, str]] = []
    for line in sections[-1].splitlines():
        m = re.match(r"^\| ([\d.]+) \| (.+) \| (topic|subpage) \|$", line)
        if m:
            rows.append((m.group(1), m.group(2), m.group(3)))
    return rows


def build_section(repo: str, rows: list[tuple[str, str, str]], when: str, run_ref: str) -> str:
    topics = sum(1 for r in rows if r[2] == "topic")
    subpages = sum(1 for r in rows if r[2] == "subpage")
    table = "\n".join(f"| {n} | {t} | {k} |" for n, t, k in rows)
    date = when[:10]
    return f"""
## Harvest — {date} ({run_ref})

- source_surface: DeepWiki.com
- repo: {repo}
- retrieved_at: {when}
- tool: read_wiki_structure (https://mcp.deepwiki.com/mcp, public, no credential)
- evidence_class: generated-external
- trust_note: DeepWiki content is a generated wiki over an index snapshot, not HEAD — verify any claim against repo source before citing it. The structure tool exposes no index/snapshot date; none is recorded.
- scope: structure only (topic list). Page contents were not harvested (T2, separately gated).

| # | Topic | Level |
|---|---|---|
{table}

Counts: {topics} topics, {subpages} subpages, {topics + subpages} pages total.
"""


def build_not_indexed_section(repo: str, when: str, run_ref: str) -> str:
    date = when[:10]
    return f"""
## Harvest — {date} ({run_ref})

- source_surface: DeepWiki.com
- repo: {repo}
- retrieved_at: {when}
- tool: read_wiki_structure (https://mcp.deepwiki.com/mcp, public, no credential)
- status: not_indexed — the public MCP returned no structure for this repo. No structure is recorded and none is fabricated. Indexing is triggered on deepwiki.com's side; there is no credential route on this surface.
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=DEFAULT_REPO)
    ap.add_argument("--record", default=DEFAULT_RECORD)
    ap.add_argument("--run-ref", default="automated harvest")
    ap.add_argument("--force", action="store_true", help="append a section even if unchanged")
    args = ap.parse_args()

    when = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    record_path = Path(args.record)
    record_text = record_path.read_text(encoding="utf-8") if record_path.exists() else ""

    text = fetch_structure(args.repo)
    if text is None:
        if "status: not_indexed" in record_text.split("\n## Harvest — ")[-1]:
            print("not_indexed (already the latest recorded state); record unchanged")
            return 0
        record_path.write_text(
            record_text.rstrip("\n") + "\n" + build_not_indexed_section(args.repo, when, args.run_ref),
            encoding="utf-8",
        )
        print("not_indexed: recorded")
        return 0

    rows = parse_structure(text)
    if not rows:
        print("structure response parsed to zero rows; treating as not_indexed", file=sys.stderr)
        return 1
    if not args.force and latest_section_rows(record_text) == rows:
        print(f"unchanged: {len(rows)} pages match the latest harvest section")
        return 0
    record_path.write_text(
        record_text.rstrip("\n") + "\n" + build_section(args.repo, rows, when, args.run_ref),
        encoding="utf-8",
    )
    print(f"harvested: appended section with {len(rows)} pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
