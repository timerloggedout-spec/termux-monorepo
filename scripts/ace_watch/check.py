#!/usr/bin/env python3
"""ACE watch checker — has Agent Compute Engine's availability moved?

Fetches Google's own ACE pages (announcement + deep dive) and looks
for availability language that differs from the announced state
recorded 2026-10-26 ("preview in the coming months", no pricing).
Pure classifier (`classify`) is unit-tested; the fetch layer is a
thin urllib wrapper. Used by .github/workflows/ace-watch.yml, which
opens an `ace-watch` issue when this script reports a signal — a
lane then verifies firsthand and updates
docs/ops/AGENT-COMPUTE-ENGINE-COMPARISON-2026-10-26.md by PR.
Detection is a tripwire, not evidence: blog wording changes are a
reason to look, never a conclusion.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.request

PAGES = [
    "https://cloud.google.com/blog/topics/ai-infrastructure/introducing-agent-compute-engine-and-expanded-agent-governance",
    "https://cloud.google.com/blog/topics/ai-infrastructure/agent-compute-engine-deep-dive",
]

# Phrases that would mean the announced state has moved. Deliberately
# narrow: the baseline "available in preview in the coming months"
# must NOT match.
SIGNALS = {
    "ga": [r"generally available", r"\bnow available\b.{0,60}agent compute engine",
           r"agent compute engine.{0,60}\bnow available\b"],
    "preview_open": [r"preview is (now )?(open|available|live)",
                     r"now in preview", r"public preview",
                     r"sign up for (the )?preview.{0,40}(now|today)"],
    "pricing": [r"agent compute engine.{0,80}pricing", r"pricing.{0,80}agent compute engine",
                r"\$\d+(\.\d+)?\s*(per|/)\s*(hour|session|agent)"],
}

BASELINE_PHRASES = ["coming months"]


def _text(html: str) -> str:
    html = re.sub(r"(?is)<script.*?</script>|<style.*?</style>", " ", html)
    text = re.sub(r"(?s)<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", text).lower()


def classify(pages_text: str) -> dict:
    """Return {signals: [...], baseline_intact: bool} for page text."""
    text = _text(pages_text)
    found = []
    for kind, patterns in SIGNALS.items():
        if any(re.search(p, text) for p in patterns):
            found.append(kind)
    return {
        "signals": found,
        "baseline_intact": all(p in text for p in BASELINE_PHRASES),
        "moved": bool(found),
    }


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "ace-watch/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode(errors="replace")


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    texts = []
    errors = []
    for url in PAGES:
        try:
            texts.append(fetch(url))
        except Exception as exc:  # fetch failure is reported, not hidden
            errors.append(f"{url}: {exc}")
    if errors and not texts:
        print(json.dumps({"moved": False, "signals": [], "errors": errors}))
        return 1
    result = classify("\n".join(texts))
    result["errors"] = errors
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
