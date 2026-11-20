#!/usr/bin/env python3
import json, sys, re
from pathlib import Path
from collections import Counter

HOME = Path.home()
MAP_DIR = HOME / 'workspace/llm_map'
INDEX = MAP_DIR / 'llm_index_compact.jsonl'
FUNC = MAP_DIR / 'func_index.jsonl'

def load_index():
    entries = {}
    with open(INDEX) as f:
        for line in f:
            e = json.loads(line)
            entries[e['p']] = e
    return entries

def load_funcs():
    funcs = []
    with open(FUNC) as f:
        for line in f:
            funcs.append(json.loads(line))
    return funcs

def tokenize(text):
    return re.findall(r'[a-zA-Z0-9_]+', text.lower())

def score_projects(query, entries, funcs):
    tokens = tokenize(query)
    project_scores = Counter()
    for fn in funcs:
        name_lower = fn['name'].lower()
        for t in tokens:
            if t in name_lower:
                proj = entries.get(fn['file'], {}).get('pj', 'unknown')
                project_scores[proj] += 1
    for path, e in entries.items():
        path_lower = path.lower()
        for t in tokens:
            if t in path_lower:
                proj = e.get('pj', 'unknown')
                project_scores[proj] += e.get('by', 0) + 1
    return project_scores

def suggest_agent(project):
    mapping = {
        'deepcli': 'deepcli-tui / deepcli send',
        'cli-synthegration': 'synthegration search / orchestrator',
        'harmony_hub': 'harmony_hub agent task',
        'harmonizer-prod_cli': 'harmonizer workspace',
        'termux-multi-agent': 'termux-multi-agent orchestration',
        'deepseek_harvest_work': 'harvest.py',
        'deepcli-tui': 'deepcli-tui',
    }
    for key, val in mapping.items():
        if key in project:
            return val
    return 'general purpose agent (fallback)'

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python manager_agent.py \"your question or topic\"")
        sys.exit(1)
    query = ' '.join(sys.argv[1:])
    entries = load_index()
    funcs = load_funcs()
    scores = score_projects(query, entries, funcs)
    if not scores:
        print("No relevant project found. Try a more specific query.")
        sys.exit(0)
    best_project, _ = scores.most_common(1)[0]
    print(f"Best-matching project: {best_project}")
    print(f"Suggested agent: {suggest_agent(best_project)}")
    print(f"Scores: {dict(scores.most_common(5))}")
