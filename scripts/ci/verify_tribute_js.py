#!/usr/bin/env python3
"""Syntax-check dashboard JavaScript and inline scripts without executing them."""
from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DASHBOARD = ROOT / "apps" / "tribute-dashboard"
SCRIPT_RE = re.compile(r"<script\b([^>]*)>(.*?)</script\s*>", re.I | re.S)
PAGES = (
    "algorithm-suite.html",
    "delphic-graph.html",
    "markov-trellis.html",
)


def main() -> int:
    checked = 0
    direct = (
        DASHBOARD / "versioning.js",
        DASHBOARD / "markov-engine.mjs",
    )
    with tempfile.TemporaryDirectory(prefix="tribute-js-check-") as temp:
        temp_path = Path(temp)
        for source in direct:
            subprocess.run(["node", "--check", str(source)], check=True)
            checked += 1
        for page_name in PAGES:
            html = (DASHBOARD / page_name).read_text(encoding="utf-8")
            for index, (attrs, body) in enumerate(SCRIPT_RE.findall(html)):
                if re.search(r"\bsrc\s*=", attrs, re.I):
                    continue
                if re.search(r"""type=["']application/ld\+json["']""", attrs, re.I):
                    continue
                suffix = ".mjs" if re.search(r"""type=["']module["']""", attrs, re.I) else ".js"
                script = temp_path / f"{page_name}-{index}{suffix}"
                script.write_text(body, encoding="utf-8")
                subprocess.run(["node", "--check", str(script)], check=True)
                checked += 1
    print(f"OK: syntax-checked {checked} dashboard JavaScript units")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
