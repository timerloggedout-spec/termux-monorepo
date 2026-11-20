
#!/usr/bin/env python3
"""Update ELO ratings based on run_history verdicts."""
import sys, json, sqlite3
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path.home() / 'cli-synthegration'))
try:
    from success_metrics import RefactorELO
except ImportError:
    print("Warning: RefactorELO not found, using placeholder")
    RefactorELO = None

DB = Path.home() / 'termux-multi-agent' / 'local_repo.db'
RATINGS_FILE = Path.home() / 'harmony_hub' / 'workspace' / 'elo' / 'elo_ratings.json'

def load_ratings():
    if RATINGS_FILE.exists():
        with open(RATINGS_FILE) as f:
            return json.load(f)
    return {}

def save_ratings(ratings):
    with open(RATINGS_FILE, 'w') as f:
        json.dump(ratings, f, indent=2)

def update():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.execute("SELECT * FROM run_history WHERE verdict IS NOT NULL ORDER BY timestamp")
    ratings = load_ratings()
    for row in cur:
        agent_id = row['agent_id'] if 'agent_id' in row.keys() else 'default_agent'
        if agent_id not in ratings:
            ratings[agent_id] = 1000  # starting ELO
        score = ratings[agent_id]
        if row['verdict'] == 'success':
            score += 10
        elif row['verdict'] == 'failure':
            score -= 15
        else:  # partial
            score += 2
        ratings[agent_id] = score
    save_ratings(ratings)
    print("ELO updated:", ratings)
    conn.close()

if __name__ == '__main__':
    update()
