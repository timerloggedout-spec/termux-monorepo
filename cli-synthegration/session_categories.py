#!/usr/bin/env python3
"""Auto‑categorize DeepSeek sessions by title and content patterns."""
import sys, json, re
from pathlib import Path
from collections import defaultdict

HOME = Path.home()
CATEGORIES = {
    "testing": ["test", "debug", "fix", "error", "fail", "traceback", "assert"],
    "refactoring": ["refactor", "refactoring", "rewrite", "clean", "restructur"],
    "development": ["build", "implement", "create", "develop", "coding", "code", "script"],
    "research": ["research", "analy", "investigat", "explor", "survey", "arxiv"],
    "configuration": ["config", "setup", "install", "deploy", "environment", "termux"],
    "data": ["data", "export", "import", "json", "csv", "database", "sql"],
    "ui": ["ui", "frontend", "html", "css", "react", "vue", "design", "layout"],
    "api": ["api", "endpoint", "rest", "graphql", "fetch", "request"],
    "documentation": ["document", "readme", "guide", "tutorial", "explain"],
}

class SessionCategorizer:
    def __init__(self):
        self.index: dict[str, list] = defaultdict(list)  # category -> [(sid, title, score)]
        self._load_live()
    
    def _load_live(self):
        """Load from live API sessions."""
        sys.path.insert(0, str(HOME / 'deepcli'))
        from deepcli.core import get_token, fetch_sessions
        try:
            token = get_token()
            sessions = fetch_sessions(token)
            for s in sessions:
                sid = s.get('id','')
                title = s.get('title','') or ''
                self._classify(sid, title)
        except Exception as e:
            print(f"Live load failed: {e}", file=sys.stderr)
    
    def _classify(self, sid: str, title: str):
        title_lower = title.lower()
        for cat, keywords in CATEGORIES.items():
            score = sum(1 for kw in keywords if kw in title_lower)
            if score > 0:
                self.index[cat].append((sid, title, score))
    
    def get(self, category: str) -> list:
        return sorted(self.index.get(category, []), key=lambda x: -x[2])
    
    def list_categories(self) -> list:
        return sorted(self.index.keys())
    
    def search_category(self, term: str) -> list:
        """Find which categories a term belongs to."""
        results = []
        term_lower = term.lower()
        for cat, sessions in self.index.items():
            for sid, title, score in sessions:
                if term_lower in title.lower():
                    results.append((cat, sid, title, score))
        return sorted(set(results), key=lambda x: -x[3])
    
    def export_index(self):
        return {cat: [(sid, title, score) for sid, title, score in sessions]
                for cat, sessions in self.index.items()}

if __name__ == "__main__":
    c = SessionCategorizer()
    if len(sys.argv) > 1:
        cat = sys.argv[1]
        sessions = c.get(cat)
        print(f"=== {cat} ({len(sessions)} sessions) ===")
        for sid, title, score in sessions[:10]:
            print(f"  {sid[:8]}... | {title[:60]}")
    else:
        for cat in c.list_categories():
            print(f"{cat}: {len(c.get(cat))} sessions")
