#!/usr/bin/env python3
"""ELO + moving average metrics for refactor pipeline success patterns."""
import json, math
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

HOME = Path.home()
METRICS_DIR = HOME / 'cli-synthegration' / 'metrics'
METRICS_DIR.mkdir(parents=True, exist_ok=True)

class RefactorELO:
    """ELO rating for refactor attempts – tracks prompt patterns and success."""
    def __init__(self, k_factor=32, base_rating=1200):
        self.k = k_factor
        self.base = base_rating
        self.ratings: dict[str, float] = {}  # pattern_hash -> elo
        self.history: list[dict] = []
        self._load()
    
    def _load(self):
        f = METRICS_DIR / 'elo_ratings.json'
        if f.exists():
            data = json.loads(f.read_text())
            self.ratings = data.get('ratings', {})
            self.history = data.get('history', [])
    
    def _save(self):
        (METRICS_DIR / 'elo_ratings.json').write_text(json.dumps({
            'ratings': self.ratings,
            'history': self.history[-200:],
            'updated': datetime.now(timezone.utc).isoformat()
        }, indent=2))
    
    def pattern_hash(self, prompt: str, language: str) -> str:
        """Create a stable hash for similar prompt patterns."""
        import hashlib
        # normalize: lowercase, strip code blocks, take keywords
        norm = prompt.lower().replace('```',' ').replace('\n',' ')
        # extract 2-3 word phrases
        words = norm.split()
        phrases = [' '.join(words[i:i+3]) for i in range(0, len(words), 3)]
        key = f"{language}:{'.'.join(phrases[:5])}"
        return hashlib.sha256(key.encode()).hexdigest()[:12]
    
    def update(self, prompt: str, language: str, success: bool, effort: int = 1):
        """Update ELO for a pattern after a refactor attempt."""
        ph = self.pattern_hash(prompt, language)
        current = self.ratings.get(ph, self.base)
        # Expected score (vs baseline 1200)
        expected = 1.0 / (1.0 + 10.0 ** ((self.base - current) / 400.0))
        score = 1.0 if success else 0.0
        new_rating = current + self.k * (score - expected) * (1 + math.log(effort + 1))
        self.ratings[ph] = round(new_rating, 1)
        self.history.append({
            'pattern_hash': ph,
            'success': success,
            'old_elo': current,
            'new_elo': new_rating,
            'effort': effort,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        self._save()
        return new_rating
    
    def top_patterns(self, n=10) -> list:
        """Return highest-rated patterns."""
        return sorted(self.ratings.items(), key=lambda x: -x[1])[:n]
    
    def moving_average(self, window=10) -> float:
        """Success rate over last N attempts."""
        recent = self.history[-window:]
        if not recent:
            return 0.5
        return sum(1 for r in recent if r['success']) / len(recent)

class ComplexityEstimator:
    """Estimate code complexity to dynamically set refactor retry limits."""
    def __init__(self):
        self.thresholds = {
            'low': 3,      # max 3 retries for simple code
            'medium': 5,   # max 5 retries for moderate
            'high': 7      # max 7 retries for complex
        }
    
    def estimate(self, code: str) -> tuple[str, int]:
        """Return (complexity_level, max_retries)."""
        lines = len(code.splitlines())
        chars = len(code)
        # count defs, classes, imports as complexity signals
        import re
        defs = len(re.findall(r'^def |^async def |^class ', code, re.MULTILINE))
        imports = len(re.findall(r'^import |^from ', code, re.MULTILINE))
        score = lines * 0.3 + chars * 0.001 + defs * 5 + imports * 2
        if score < 30:
            return ('low', self.thresholds['low'])
        elif score < 100:
            return ('medium', self.thresholds['medium'])
        else:
            return ('high', self.thresholds['high'])

if __name__ == "__main__":
    elo = RefactorELO()
    comp = ComplexityEstimator()
    print(f"Top patterns by ELO: {elo.top_patterns(5)}")
    print(f"Moving average (last 10): {elo.moving_average():.2f}")
    print(f"Complexity test: {comp.estimate('def foo():\\n    return 1')}")
