#!/usr/bin/env python3
"""Router Agent — direct your query to the best project/agent/sprint, with --foresight"""
import json, sys, re, subprocess
from pathlib import Path
from collections import Counter

HOME = Path.home()
MAP = HOME / 'workspace/llm_map'
INDEX = MAP / 'llm_index_compact.jsonl'
FUNC = MAP / 'func_index.jsonl'
SPRINTS = HOME / 'cli-synthegration/metrics/sprints.json'
FORGE = HOME / 'workspace/FORGE_OVERSIGHT.md'

# ── Data loaders ────────────────────────────────────────
def load_json(path):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}

def load_index():
    entries = {}
    if INDEX.exists():
        with open(INDEX) as f:
            for line in f:
                e = json.loads(line)
                entries[e['p']] = e
    return entries

def load_funcs():
    if FUNC.exists():
        with open(FUNC) as f:
            return [json.loads(line) for line in f]
    return []

# ── Helpers ──────────────────────────────────────────────
def tokenize(text):
    return set(re.findall(r'[a-zA-Z0-9_]{2,}', text.lower()))

def sprint_action(sprint):
    return sprint.get('action') or sprint.get('resolution') or ''

def sprint_text(sprint):
    return (sprint.get('name','') + ' ' +
            sprint_action(sprint) + ' ' +
            sprint.get('blocker','')).lower()

# ── Core scoring & routing ──────────────────────────────
def score_projects(query, entries, funcs):
    tokens = tokenize(query)
    project_scores = Counter()
    for fn in funcs:
        name_tokens = tokenize(fn['name'])
        if tokens & name_tokens:
            proj = entries.get(fn['file'], {}).get('pj', 'unknown')
            project_scores[proj] += 2
    for path, e in entries.items():
        path_tokens = tokenize(path)
        if tokens & path_tokens:
            proj = e.get('pj', 'unknown')
            project_scores[proj] += e.get('by', 0) + 1
    for p in list(project_scores.keys()):
        if p.startswith('.hermes') or p.startswith('.cargo'):
            project_scores[p] = 0
    return project_scores

def suggest_agent(project):
    mapping = {
        'deepcli': ('deepcli-tui', 'deepcli send'),
        'cli-synthegration': ('synthegration', 'synthegration search / orchestrator'),
        'harmony_hub': ('harmony_hub', 'harmony_hub agent task'),
        'harmonizer-prod_cli': ('harmonizer', 'harmonizer workspace'),
        'termux-multi-agent': ('termux-multi-agent', 'run.py / provision_agent.py'),
        'deepseek_harvest_work': ('harvest', 'harvest.py'),
        'deepcli-tui': ('deepcli-tui', 'deepcli-tui / deepcli send'),
    }
    for key, (short, cmd) in mapping.items():
        if key in project:
            return short, cmd
    return ('general', 'general purpose agent (fallback)')

def match_sprints(tokens, sprints):
    return [s for s in sprints if any(t in sprint_text(s) for t in tokens)]

def match_delegations(tokens, forge_text):
    matches = []
    in_table = False
    for line in forge_text.split('\n'):
        if '## Active Delegations' in line:
            in_table = True
            continue
        if in_table and line.startswith('|'):
            if any(t in line.lower() for t in tokens):
                matches.append(line.strip())
        if in_table and not line.startswith('|'):
            break
    return matches

# ── ForeSight output builder ────────────────────────────
def show_foresight(best, funcs, entries):
    fs_file = MAP / 'foresight_state.json'
    if not fs_file.exists():
        print("\n⚠️  ForeSight state not found. Run foresight_collect.py first.")
        return
    with open(fs_file) as f:
        fstate = json.load(f)

    # Domain map
    print(f"\n# 🌐 Domain Map for {best}")
    project_funcs = [fn for fn in funcs if entries.get(fn['file'], {}).get('pj') == best]
    domain_files = {}
    for fn in project_funcs:
        domain_files.setdefault(fn['file'], []).append(fn['name'])
    top_files = sorted(domain_files.items(), key=lambda x: -len(x[1]))[:8]
    for f, names in top_files:
        print(f"  {f} ({len(names)} functions): {', '.join(names[:4])}{'...' if len(names)>4 else ''}")

    # Readiness scores
    staged = {k: v for k, v in fstate.get('readiness', {}).get('scores', {}).items() if best in k}
    if staged:
        print(f"\n# 📊 Readiness Scores ({best})")
        for f, score in sorted(staged.items(), key=lambda x: -x[1])[:5]:
            ripe = '🍑' if score >= 80 else '  '
            print(f"  {ripe} {f}: {score}/100")

    # Bottlenecks
    bottlenecks = [b for b in fstate.get('sprints', {}).get('bottlenecks', []) if best in b.get('id','') or best in b.get('name','').lower()]
    if bottlenecks:
        print(f"\n# ⚠️ Bottlenecks affecting {best}")
        for b in bottlenecks:
            print(f"  [{b.get('impact','?')}] {b['name']}: {b['blocker']}")

# ── Main ─────────────────────────────────────────────────
if __name__ == '__main__':
    args = sys.argv[1:]
    foresight_mode = False
    if args and args[0] == '--foresight':
        foresight_mode = True
        args = args[1:]
    if not args:
        print("Usage: python3 router_agent.py [--foresight] \"your question or topic\"")
        sys.exit(1)
    query = ' '.join(args)
    tokens = tokenize(query)

    entries = load_index()
    funcs = load_funcs()
    sprints = load_json(SPRINTS)
    forge_text = FORGE.read_text() if FORGE.exists() else ""

    scores = score_projects(query, entries, funcs)
    if not scores or max(scores.values()) == 0:
        print("No matching project found.\nTry a broader term, or check session cache below.")
        sys.exit(0)

    best, score = scores.most_common(1)[0]
    agent_name, agent_cmd = suggest_agent(best)

    print(f"Query: {query}")
    print(f"\n→ Best project: {best} (score {score})")
    print(f"→ Suggested agent: {agent_name}")
    print(f"→ Command: {agent_cmd}")

    # Sprint matches
    if sprints:
        matched = match_sprints(tokens, sprints)
        if matched:
            print(f"\n🔹 Active sprints matching your query:")
            for s in matched[:3]:
                act = sprint_action(s)
                line = f"  [{s.get('status','?')}] {s.get('name','')}"
                if act:
                    line += f": {act[:80]}"
                print(line)

    # Delegation matches
    matched_del = match_delegations(tokens, forge_text)
    if matched_del:
        print(f"\n🔹 FORGE delegations:")
        for line in matched_del[:3]:
            print(f"  {line}")

    # ForeSight output
    if foresight_mode:
        show_foresight(best, funcs, entries)
        # Impact Oracle: if query contains a file-like token, show its shockwave
        for word in query.split():
            if '/' in word and '.' in word and not word.startswith('http'):
                oracle = MAP / 'impact_oracle.py'
                if oracle.exists():
                    try:
                        result = subprocess.run(
                            ['python3', str(oracle), word],
                            capture_output=True, text=True, timeout=10
                        )
                        if result.returncode == 0 and result.stdout.strip():
                            print(f"\n# 💥 Shockwave Index for {word}")
                            print(result.stdout)
                    except Exception:
                        pass
                break

    # Search cached sessions for matching conversations
    for d in [HOME / '.deepcli/session_store', HOME / 'storage/downloads/synthegration_exports']:
        if not d.exists(): continue
        for f in sorted(d.glob('*.json'), key=lambda x: x.stat().st_mtime if x.is_file() else 0, reverse=True)[:50]:
            try:
                data = json.loads(f.read_text()[:5000])
                msgs = data if isinstance(data, list) else data.get('messages', [])
                if msgs:
                    first = msgs[0].get('content', '')[:150] if isinstance(msgs[0], dict) else str(msgs[0])[:150]
                    if any(w.lower() in first.lower() for w in query.lower().split()):
                        sid = f.stem if f.is_file() else f.name
                        print(f"  📂 Session: {sid[:32]}... — {first[:80]}")
            except: pass
    # Search cached sessions
    for d in [HOME / '.deepcli/session_store', HOME / 'storage/downloads/synthegration_exports']:
        if not d.exists(): continue
        for f in sorted(d.glob('*.json'), key=lambda x: x.stat().st_mtime if x.is_file() else 0, reverse=True)[:30]:
            try:
                data = json.loads(f.read_text()[:5000])
                msgs = data if isinstance(data, list) else data.get('messages', [])
                if msgs:
                    first = msgs[0].get('content', '')[:150]
                    if any(w.lower() in first.lower() for w in query.lower().split()):
                        print(f"  📂 Session: {f.stem[:32]}... — {first[:80]}")
            except: pass
    print(f"\nFull project scores: {dict(scores.most_common(5))}")
