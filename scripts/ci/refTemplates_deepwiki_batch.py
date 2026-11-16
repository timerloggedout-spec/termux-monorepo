#!/usr/bin/env python3
"""Batch DeepWiki signals for refTemplates candidates (public MCP path).

Boundary (same as reconcile_devin_wiki_access.py):
  - Devin App access makes repos *eligible* for provider indexing.
  - This script does NOT call undocumented private index APIs.
  - Public content: DeepWiki MCP https://mcp.deepwiki.com/mcp
    tools: read_wiki_structure, read_wiki_contents, ask_question.

Default mode is dry-run schema emission so CI stays network-free unless --live.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
MCP_URL = "https://mcp.deepwiki.com/mcp"


def dry_entry(full_name: str) -> dict:
    return {
        "repository": full_name,
        "mode": "dry_run",
        "wiki_structure": None,
        "detail": "Network harvest skipped; pass --live to call public DeepWiki MCP",
        "collected_at": datetime.now(UTC).isoformat(),
        "public_deepwiki": "provider-managed; no documented indexing-write endpoint is invoked",
    }


def live_structure(full_name: str, timeout: float = 20.0) -> dict:
    """Best-effort JSON-RPC-ish probe. DeepWiki MCP wire may vary; failures stay soft."""
    # Streamable HTTP MCP often expects session protocol; keep this as a soft probe.
    body = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "read_wiki_structure",
                "arguments": {"repo": full_name},
            },
        }
    ).encode("utf-8")
    req = Request(
        MCP_URL,
        data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        return {
            "repository": full_name,
            "mode": "live",
            "http_ok": True,
            "raw_preview": raw[:2000],
            "collected_at": datetime.now(UTC).isoformat(),
            "public_deepwiki": "provider-managed; no documented indexing-write endpoint is invoked",
        }
    except (URLError, TimeoutError, OSError) as exc:
        return {
            "repository": full_name,
            "mode": "live",
            "http_ok": False,
            "detail": str(exc),
            "collected_at": datetime.now(UTC).isoformat(),
            "public_deepwiki": "provider-managed; no documented indexing-write endpoint is invoked",
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repos",
        nargs="*",
        default=["Yeachan-Heo/My-Jogyo", "saim-x/opencode-research-papers", "cactus-compute/needle"],
        help="owner/name public repos to probe",
    )
    parser.add_argument("--live", action="store_true", help="Call public DeepWiki MCP (network)")
    parser.add_argument("--output", type=Path, help="JSONL out")
    args = parser.parse_args()

    rows = [live_structure(r) if args.live else dry_entry(r) for r in args.repos]
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r, sort_keys=True) + "\n")
        print(f"OK: deepwiki batch {len(rows)} → {args.output} mode={'live' if args.live else 'dry_run'}")
    else:
        for r in rows:
            print(json.dumps(r, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
