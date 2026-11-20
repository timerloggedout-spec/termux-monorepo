#!/usr/bin/env python3
"""4_51GH7 Impact Oracle — Shockwave Index, Nexus Rank & Grimoire Frames

Uses the official GRIMOIRE_DICTIONARY.md plus 4_51GH7 extensions
for advanced scoring: Shockwave, Nexus, Echo, Forged Stability.
"""
import json, sys, os, re
from pathlib import Path
from collections import defaultdict, deque
from datetime import datetime, timezone

HOME = Path.home()
GRAPH = Path('file_graph.json')
INDEX = Path('llm_index_compact.jsonl')
RUN_HISTORY = HOME / 'termux-multi-agent/run_history.jsonl'
GRIMOIRE_MD = HOME / 'harmony_hub/config/GRIMOIRE_DICTIONARY.md'

# ── Load the real Grimoire Dictionary ─────────────────
def load_grimoire():
    terms = {}
    if not GRIMOIRE_MD.exists():
        return terms
    text = GRIMOIRE_MD.read_text()
    in_table = False
    for line in text.split('\n'):
        if '1337SP3@K' in line and 'Grimoire' in line:
            in_table = True
            continue
        if in_table and line.startswith('|') and '`' in line:
            cols = [c.strip().strip('`') for c in line.split('|') if c.strip()]
            if len(cols) >= 2:
                leet, grim = cols[0], cols[1]
                terms[leet] = grim
        if in_table and not line.startswith('|'):
            break
    return terms

GRIMOIRE = load_grimoire()

# Map our concepts to Grimoire terms (preferring official ones)
GRIM_TERMS = {
    'shockwave': GRIMOIRE.get('shockwave', 'Shockwave Index'),   # no official; 4_51GH7 extension
    'nexus':     GRIMOIRE.get('nexus', 'Nexus Rank'),            # 4_51GH7 extension
    'echo':      GRIMOIRE.get('3ch0', 'Echo'),                  # official: 3ch0 → Echo
    'forge':     GRIMOIRE.get('forge', 'Forged Stability'),      # 4_51GH7 extension
    'entropy':   GRIMOIRE.get('entropy', 'Entropy Score'),       # 4_51GH7 extension
    'ripple':    GRIMOIRE.get('ripple', 'Ripple Cascade'),       # 4_51GH7 extension
    'anchor':    GRIMOIRE.get('anchor', 'Anchor Count'),         # 4_51GH7 extension
    'convergence': GRIMOIRE.get('convergence', 'Convergence Weight'), # 4_51GH7
}

# ── Data loaders ──────────────────────────────────────
def load_index():
    entries = {}
    if INDEX.exists():
        with open(INDEX) as f:
            for line in f:
                e = json.loads(line)
                entries[e['p']] = e
    return entries

def load_graph():
    if not GRAPH.exists():
        return {}
    with open(GRAPH) as f:
        return json.load(f)

def load_run_history():
    if not RUN_HISTORY.exists():
        return []
    with open(RUN_HISTORY) as f:
        return [json.loads(line) for line in f]

def get_project(file_path, entries):
    return entries.get(file_path, {}).get('pj', 'unknown')

def build_reverse_graph(graph):
    reverse = defaultdict(set)
    for src, targets in graph.items():
        for tgt in targets:
            reverse[tgt].add(src)
    return reverse

# ── Scoring engines (Grimoire‑flavoured) ──────────────

def shockwave(target, reverse_graph, entries, max_depth=5):
    """BFS: all files that import this file (direct + transitive)."""
    visited = set()
    queue = deque([(target, 0)])
    affected = []
    while queue:
        current, depth = queue.popleft()
        if current in visited or depth > max_depth:
            continue
        visited.add(current)
        if current != target:
            affected.append((current, depth))
        for dependent in reverse_graph.get(current, []):
            if dependent not in visited:
                queue.append((dependent, depth + 1))
    return affected

def nexus_rank(target, reverse_graph, run_history):
    """
    PageRank‑inspired importance:
    Only validated dependents contribute.
    Each dependent with >=1 PASS gives weight = 1 + log2(1+pass_count).
    Sum those weights, scale to 0–100 (cap at 10 validated dependents as 100).
    """
    direct = reverse_graph.get(target, set())
    import math
    total_weight = 0.0
    validated = 0
    for f in direct:
        passes = sum(1 for e in run_history if e.get('target_file') == f and e.get('verdict','').upper() == 'PASS')
        if passes > 0:
            weight = 1 + math.log2(1 + passes)
            total_weight += weight
            validated += 1
    # Scale: 10 validated dependents with average weight ~1 → max 100
    nexus_score = min(100, round(total_weight * 10))
    return nexus_score, validated, len(direct)

def echo_return(target, run_history):
    """How many PASS verdicts does this file itself have?"""
    return sum(1 for e in run_history if e.get('target_file') == target and e.get('verdict','').upper() == 'PASS')

def forged_stability(target, run_history):
    """Days since last FAIL verdict (or days since first PASS if never failed)."""
    fails = [e for e in run_history if e.get('target_file') == target and e.get('verdict','').upper() == 'FAIL']
    if not fails:
        passes = [e for e in run_history if e.get('target_file') == target]
        if passes:
            oldest = min(e.get('timestamp','') for e in passes)
            try:
                first = datetime.fromisoformat(oldest)
                return (datetime.now(timezone.utc) - first).days
            except:
                pass
        return 0
    latest_fail = max(fails, key=lambda e: e.get('timestamp',''))
    try:
        fail_date = datetime.fromisoformat(latest_fail['timestamp'])
        return (datetime.now(timezone.utc) - fail_date).days
    except:
        return 0

# ── Main ─────────────────────────────────────────────
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 impact_oracle.py <file_path>")
        sys.exit(1)

    target = sys.argv[1]
    if os.path.isabs(target):
        try:
            target = str(Path(target).relative_to(HOME))
        except ValueError:
            pass

    entries = load_index()
    graph = load_graph()
    reverse = build_reverse_graph(graph)

    # Compute Data Reach (all variables in scope)
    data_reach = 0
    graph_deps = 0
    total_reach = 0
    chunks_dir = HOME / 'cli-synthegration/workspace/correlation/chunks'
    if chunks_dir.exists():
        import gzip
        chunk_file = chunks_dir / 'correlations.json.gz'
        if chunk_file.exists():
            target_bytes = target.encode()
            with gzip.open(chunk_file, 'rb') as gf:
                for lb in gf:
                    if target_bytes in lb:
                        data_reach += 1
    graph_deps = len(reverse.get(target, set()))
    total_reach = data_reach + graph_deps

    if target not in entries:
        print(f"⚠️  File '{target}' not in master index.")
        sys.exit(1)

    # ── Shockwave Index (destructive potential) ──
    affected = shockwave(target, reverse, entries)
    direct = sorted(reverse.get(target, set()))
    proj_direct = defaultdict(list)
    for f in direct:
        proj_direct[get_project(f, entries)].append(f)
    projects = {get_project(f, entries) for f, _ in affected}
    shock_score = min(100, len(affected) * 5 + len(projects) * 10)

    # ── Nexus Rank (constructive importance, PageRank‑like) ──

    # Load run history for Nexus scoring
    run_history = load_run_history()
    nexus_score, nexus_validated, nexus_direct = nexus_rank(target, reverse, run_history)

    # ── Echo Return ──
    echo = echo_return(target, run_history)

    # ── Forged Stability ──
    stability_days = forged_stability(target, run_history)
    stability_score = min(100, stability_days * 2)

    # ── Composite Reliability (Convergence Weight) ──
    reliability = min(100, nexus_score + stability_score + echo * 5)

    # ── Output ──
    print(f"📄 File: {target}")
    print(f"   Project: {entries[target].get('pj','unknown')} | Anchor (used_by): {entries[target].get('by',0)}")
    print()

    # Frame: Shockwave
    print(f"💥 {GRIM_TERMS['shockwave']}: {shock_score}/100")
    print(f"   Direct dependents: {len(direct)} files across {len(proj_direct)} projects")
    print(f"   {GRIM_TERMS['ripple']}: {len(affected)} files across {len(projects)} projects")
    for proj, files in sorted(proj_direct.items()):
        print(f"      [{proj}] {len(files)} direct")
    print()
    # 📚 Data Reach (computed above)
    try:
        print(f"📚 Data Reach: {total_reach} total ({graph_deps} imports, {data_reach} data references)")
    except NameError:
        pass
    # Frame: Entropy (staged files)
    foresight_file = Path('foresight_state.json')
    if foresight_file.exists():
        with open(foresight_file) as fs:
            fstate = json.load(fs)
        staged = fstate.get('readiness', {}).get('scores', {})
        affected_staged = [f for f, _ in affected if f in staged]
        if affected_staged:
            print(f"🔥 {GRIM_TERMS['entropy']}: {len(affected_staged)} staged files in shockwave")
            for f in affected_staged[:8]:
                score_val = staged[f]
                ripe = '🍑' if score_val >= 80 else '  '
                print(f"   {ripe} {f} (readiness {score_val})")
        else:
            print("✅ No staged files in shockwave.")

    # Verdict
    print()
    if shock_score >= 80 and reliability < 40:
        print("⚠️  HIGH SHOCKWAVE + LOW RELIABILITY — promote with extreme caution.")
    elif shock_score < 40 and reliability >= 80:
        print("✅ LOW SHOCKWAVE + HIGH RELIABILITY — safe to promote.")
    elif shock_score >= 80 and reliability >= 80:
        print("🔱 HIGH IMPACT + HIGH RELIABILITY — critical nexus component; requires full validation suite.")
    else:
        print("ℹ️  Standard component — evaluate individual criteria before promotion.")
    # Log metrics
    log_entry = {
        "file": target,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "shockwave": shock_score,
        "nexus": nexus_score,
        "reliability": reliability,
        "stability_days": stability_days,
        "echo": echo,
        "staged_in_blast": len(affected_staged) if 'affected_staged' in dir() else 0
    }
    metrics_path = HOME / 'workspace/llm_map/metrics_log.jsonl'
    with open(metrics_path, 'a') as mlf:
        mlf.write(json.dumps(log_entry) + '\n')
    print(f"📊 Metrics logged to metrics_log.jsonl")
