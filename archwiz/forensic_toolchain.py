#!/usr/bin/env python3
"""Forensic Toolchain – fragment match, similarity scan, correlation scout, staged extraction."""
import json, sys, re, hashlib, difflib
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
PROV = HOME / 'cli-synthegration/workspace/provenance/comprehensive_provenance.json'
TRUE_VER = HOME / 'cli-synthegration/workspace/provenance/true_versions.json'
RUN_HIST = HOME / 'termux-multi-agent/run_history.jsonl'
EXPORT_SOURCES = [
    HOME / "storage/downloads/_doing/_1-build/DeepSeek/exports/deepseek_data-2026-05-26/conversations.json",
    HOME / "storage/downloads/_doing/_1-build/DeepSeek/exports/deepseek_data-2026-05-17/conversations.json",
    HOME / "deepseek_harvest_work/export.json",
]

EXPORT_SOURCES = [
    HOME / "storage/downloads/_doing/_1-build/DeepSeek/exports/deepseek_data-2026-05-26/conversations.json",
    HOME / "storage/downloads/_doing/_1-build/DeepSeek/exports/deepseek_data-2026-05-17/conversations.json",
    HOME / "deepseek_harvest_work/export.json",
]

# Additional sources: all synthegration_exports manifest.json files
def _load_export_sources():
    extra = []
    exports_dir = HOME / "storage/downloads/synthegration_exports"
    if exports_dir.is_dir():
        for d in exports_dir.iterdir():
            m = d / "manifest.json"
            if m.exists():
                extra.append(m)
    return extra
STAGING = HOME / 'archwiz/staging_blocks.json'

R = '\033[1;31m'; G = '\033[1;32m'; Y = '\033[1;33m'; C = '\033[1;36m'; N = '\033[0m'

def load_code_blocks():
    blocks = []
    for cf in EXPORT_SOURCES + _load_export_sources():
        if not cf.exists(): continue
        with open(cf) as f: data = json.load(f)
        for conv in (data if isinstance(data, list) else [data]):
            sid = conv.get('id') or conv.get('title','?')
            for nid, node in conv.get('mapping',{}).items():
                msg = node.get('message')
                if not isinstance(msg, dict): continue
                ts = msg.get('inserted_at')
                utc_ts = None
                if ts:
                    try: utc_ts = datetime.fromisoformat(str(ts).replace('Z','+00:00')).timestamp()
                    except: pass
                content = ''
                for frag in msg.get('fragments', []):
                    if isinstance(frag, dict): content += frag.get('content','') + '\n'
                for bi, block in enumerate(re.findall(r"```(?:\w+)?\n(.*?)\n```", content, re.DOTALL)):
                    blocks.append({
                        'session': str(sid), 'node_id': nid, 'block_idx': bi,
                        'timestamp_utc': utc_ts, 'text': block,
                        'hash': hashlib.sha256(block.strip().encode()).hexdigest(),
                    })
    return blocks

def fragment_match(search_term):
    """Find code blocks containing the search term."""
    blocks = load_code_blocks()
    term = search_term.strip().strip('"').strip("'")
    matches = [cb for cb in blocks if term.lower() in cb['text'][:500].lower()]
    matches.sort(key=lambda x: x['timestamp_utc'] or 0)
    print(f"{Y}Fragment Match — {len(matches)} results for '{term}'{N}\n")
    for i, m in enumerate(matches[:15]):
        ts = datetime.fromtimestamp(m['timestamp_utc'], tz=timezone.utc).strftime('%Y-%m-%d %H:%M') if m['timestamp_utc'] else 'unknown'
        print(f"  {G}#{i}{N}  [{ts}]  {m['session'][:16]}...  node={m['node_id']}")
        print(f"     {C}{m['text'][:120].replace(chr(10),' ')}{N}")
    return matches

def similarity_scan(target_text, threshold=0.3):
    """Find code blocks similar to the target text using difflib."""
    blocks = load_code_blocks()
    scored = []
    for cb in blocks:
        ratio = difflib.SequenceMatcher(None, target_text[:200], cb['text'][:200]).ratio()
        if ratio >= 0.3:
            scored.append((ratio, cb))
    scored.sort(key=lambda x: -x[0])
    print(f"{Y}Similarity Scan — {len(scored)} blocks with similarity ≥ 0.3{N}\n")
    for i, (ratio, m) in enumerate(scored[:15]):
        ts = datetime.fromtimestamp(m['timestamp_utc'], tz=timezone.utc).strftime('%Y-%m-%d %H:%M') if m['timestamp_utc'] else 'unknown'
        print(f"  {G}#{i}{N}  [{ratio:.2f}]  [{ts}]  {m['session'][:16]}...")
        print(f"     {C}{m['text'][:120].replace(chr(10),' ')}{N}")
    return scored

def correlation_scout(filepath):
    print(f"{Y}Correlation Scout — '{filepath}'{N}\n")
    if TRUE_VER.exists():
        tv = json.loads(TRUE_VER.read_text())
        if filepath in tv:
            print(f"  {G}true_versions:{N} {json.dumps(tv[filepath])[:200]}")
        else:
            print(f"  {R}true_versions: not tracked.{N}")
    if RUN_HIST.exists():
        matches = []
        with open(RUN_HIST) as f:
            for line in f:
                e = json.loads(line)
                if e.get('target_file') == filepath:
                    matches.append(e)
        if matches:
            print(f"  {G}run_history ({len(matches)}):{N}")
            for m in matches[-5:]:
                print(f"    {m.get('timestamp','')[:19]}  {m.get('verdict','?')}  by {m.get('agent','?')}")
        else:
            print(f"  {R}run_history: none.{N}")
    if PROV.exists():
        prov = json.loads(PROV.read_text())
        if filepath in prov:
            vs = prov[filepath]
            print(f"  {G}comprehensive_provenance ({len(vs)} versions):{N}")
            for v in vs[:5]:
                print(f"    [{v.get('strategy','?')}] {v.get('timestamp_utc','?')[:19]}  {v.get('session','?')[:16]}...")

def extract_block(search_term, index):
    """Extract the full code of a specific match and save to staging."""
    blocks = load_code_blocks()
    term = search_term.strip().strip('"').strip("'")
    matches = [cb for cb in blocks if term.lower() in cb['text'][:500].lower()]
    matches.sort(key=lambda x: x['timestamp_utc'] or 0)
    if 0 <= index < len(matches):
        m = matches[index]
        print(f"{Y}Full Block #{index}:{N}\n{m['text'][:3000]}")
        # Save to staging
        staging = []
        if STAGING.exists():
            staging = json.loads(STAGING.read_text())
        staging.append({
            'source': 'forensic_toolchain',
            'search_term': search_term,
            'index': index,
            'timestamp': m['timestamp_utc'],
            'session': m['session'],
            'code': m['text'],
            'hash': m['hash']
        })
        STAGING.parent.mkdir(parents=True, exist_ok=True)
        STAGING.write_text(json.dumps(staging, indent=2))
        print(f"\n{G}✅ Block staged to {STAGING}. Ready for review panel.{N}")
    else:
        print(f"{R}No match at index {index}. Run fragment match first.{N}")


def diff_blocks(search_term, idx1, idx2):
    """Show a unified diff between two extracted blocks."""
    blocks = load_code_blocks()
    term = search_term.strip().strip('"').strip("'")
    matches = [cb for cb in blocks if term.lower() in cb['text'][:500].lower()]
    matches.sort(key=lambda x: x['timestamp_utc'] or 0)
    if idx1 < len(matches) and idx2 < len(matches):
        import difflib
        a = matches[idx1]['text'].splitlines()
        b = matches[idx2]['text'].splitlines()
        diff = difflib.unified_diff(a, b, fromfile=f"#{idx1} ({matches[idx1].get('session','')[:16]}...)",
                                   tofile=f"#{idx2} ({matches[idx2].get('session','')[:16]}...)", lineterm='')
        print("\n".join(diff))
    else:
        print(f"{R}One or both indices out of range.{N}")


def message_search(term):
    """Search all exported message content (not just code blocks)."""
    from pathlib import Path
    results = []
    exports_dir = HOME / "storage/downloads/synthegration_exports"
    if exports_dir.is_dir():
        for d in sorted(exports_dir.iterdir()):
            m = d / "manifest.json"
            if not m.exists(): continue
            try:
                blocks = json.loads(m.read_text())
                if not isinstance(blocks, list): continue
            except: continue
            for b in blocks:
                if not isinstance(b, dict): continue
                code = b.get("code", "")
                if term.lower() in code.lower():
                    ts = b.get("message_timestamp", 0)
                    sid = b.get("conversation_id", d.name[:32])
                    role = b.get("message_role", "?")
                    snippet = code[:200].replace("\n", " ")
                    results.append((ts, sid, role, snippet))
    results.sort(key=lambda x: x[0] if x[0] else 0)
    print(f"Message Search — {len(results)} results for '{term}'\n")
    for i, (ts, sid, role, snippet) in enumerate(results[:15]):
        dt = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M") if ts else "unknown"
        print(f"  #{i}  [{dt}]  {sid[:16]}...  ({role})")
        print(f"     {snippet[:150]}")
        print()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: forensic_toolchain.py fragment <term> | similar <text> [threshold] | scout <file> | extract <term> <idx> | diff <term> <i1> <i2>")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == 'fragment' and len(sys.argv) > 2:
        fragment_match(' '.join(sys.argv[2:]))
    elif cmd == 'similar' and len(sys.argv) > 2:
        target = ' '.join(sys.argv[2:]).rsplit(' ', 1)
        if len(target) > 1 and target[-1].replace('.','').isdigit():
            similarity_scan(target[0], float(target[-1]))
        else:
            similarity_scan(' '.join(sys.argv[2:]))
    elif cmd == 'msg' and len(sys.argv) > 2:
        message_search(' '.join(sys.argv[2:]))
    elif cmd == 'scout' and len(sys.argv) > 2:
        correlation_scout(sys.argv[2])
    elif cmd == 'diff' and len(sys.argv) > 2:
        term = sys.argv[2]
        i1 = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        i2 = int(sys.argv[4]) if len(sys.argv) > 4 else 1
        diff_blocks(term, i1, i2)
    elif cmd == 'extract' and len(sys.argv) > 2:
        term = sys.argv[2]
        idx = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        extract_block(term, idx)
    else:
        print("Usage: forensic_toolchain.py fragment <term> | similar <text> [threshold] | scout <file> | extract <term> <idx> | diff <term> <i1> <i2>")
