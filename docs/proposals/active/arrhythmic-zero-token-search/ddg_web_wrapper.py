#!/usr/bin/env python3
"""
AZT-003 thin extract — DuckDuckGo HTML no-JS web wrapper.
Termux-friendly, zero browser automation, free/zero-token path.
Implements: AZT-003
"""
from __future__ import annotations

import json
import sys
from typing import Any

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    print(json.dumps({"error": f"missing dependency: {e}", "hint": "pip install requests beautifulsoup4"}))
    sys.exit(1)


class DDGWebWrapper:
    """Legacy HTML endpoint — resilient to many headless checks."""

    def __init__(self, timeout: float = 10.0) -> None:
        self.endpoint = "https://html.duckduckgo.com/html/"
        self.timeout = timeout
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "DNT": "1",
        }

    def search(self, query: str, max_results: int = 10) -> list[dict[str, Any]]:
        if not query or not query.strip():
            return []
        try:
            resp = requests.post(
                self.endpoint,
                data={"q": query.strip()},
                headers=self.headers,
                timeout=self.timeout,
            )
            if resp.status_code != 200:
                return [{"error": f"status {resp.status_code}"}]
            soup = BeautifulSoup(resp.text, "html.parser")
            results: list[dict[str, Any]] = []
            for result in soup.select("div.result")[:max_results]:
                title_el = result.select_one("a.result__a")
                snippet_el = result.select_one("a.result__snippet") or result.select_one(".result__snippet")
                url = title_el.get("href") if title_el else None
                title = title_el.get_text(strip=True) if title_el else ""
                snippet = snippet_el.get_text(strip=True) if snippet_el else ""
                if title or url:
                    results.append({"title": title, "url": url, "snippet": snippet})
            return results
        except Exception as exc:  # noqa: BLE001 — surface for agent loops
            return [{"error": str(exc)}]


def main() -> None:
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Termux agentic pipeline"
    wrapper = DDGWebWrapper()
    out = wrapper.search(query)
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
