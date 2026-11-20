                print(f"{i+1}. **[Promotion]** `{ts}` — session `{event['session'][:8]}…`, version hash `{event['hash']}`")
            elif src == 'test':
                verdict = event.get('verdict', '?')
                icon = '✅' if verdict == 'PASS' else '❌' if verdict == 'FAIL' else '⬜'
                print(f"{i+1}. {icon} **[Test]** `{ts}` — {verdict} by `{event['agent']}`")
                if event.get('errors'):
                    print(f"   Errors: {event['errors']}")

    # 4. Co‑evolution
    if full_mode and target_sessions:
        co_changed = defaultdict(set)
        for src, sessions in corr_map.items():
            if src == target:
                continue
            for s in sessions:
                if s in target_sessions:
                    co_changed[src].add(s)
        if co_changed:
            print(f"\n## 🌐 Co‑Evolution ({len(co_changed)} files changed in same sessions)\n")
            for co_file, co_sessions in sorted(co_changed.items()):
                print(f"- `{co_file}` ({len(co_sessions)} shared sessions)")

    # 5. Current State
    idx_path = MAP / 'llm_index_compact.jsonl'
    if idx_path.exists():
        with open(idx_path) as f:
            for line in f:
                e = json.loads(line)
                if e.get('p') == target:
                    print(f"\n## 📊 Current State")
                    print(f"- Shockwave dependents: {e.get('by', 0)}")
                    print(f"- Last modified (ts): {e.get('ts', '?')[:19]}")
                    print(f"- AST hashes: {len(e.get('ah', []))} functions hashed")
                    print(f"- Project: {e.get('pj', '?')}")
                    print(f"- Language: {e.get('l', '?')}")
                    break

    print(f"\n🏺 Archaeology complete. {len(timeline)} events reconstructed.")
PYEOF

chmod +x archaeologist.py
python3 -m py_compile archaeologist.py && echo "✅ archaeologist.py updated (bridge enabled)"
# Re‑test
python3 archaeologist.py deepcli/deepcli/core.py --full
cd ~/workspace/llm_map
# Create batch_resumer.py if not already present
if [ ! -f batch_resumer.py ]; then
cat > batch_resumer.py << 'PYEOF'
#!/usr/bin/env python3
"""BatchResumer — incremental processing with crash‑proof checkpointing."""
import json, os
from pathlib import Path
from datetime import datetime, timezone

class BatchResumer:
    def __init__(self, state_file: str, total_items: int, flush_every: int = 100):
        self.state_path = Path(state_file)
        self.total = total_items
        self.flush_every = flush_every
        self.processed = self._load_state()
        self.current = self.processed
        self.start_time = datetime.now(timezone.utc)

    def _load_state(self) -> int:
        if self.state_path.exists():
            try:
                return int(self.state_path.read_text().strip())
            except (ValueError, OSError):
                return 0
        return 0

    def _save_state(self, n: int):
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(str(n))

    def process(self, items):
        for i in range(self.processed, self.total):
            try:
                item = items[i]
            except IndexError:
                break
            self.current = i + 1
            is_checkpoint = (self.current % self.flush_every == 0) or (self.current == self.total)
            yield item, i, is_checkpoint
        self._save_state(self.current)

    def checkpoint(self, flush_fn=None):
        self._save_state(self.current)
        if flush_fn:
            flush_fn()
        elapsed = (datetime.now(timezone.utc) - self.start_time).total_seconds()
        pct = (self.current / self.total * 100) if self.total else 0
        print(f"  🔄 {self.current}/{self.total} ({pct:.1f}%) — {elapsed:.0f}s elapsed", end='\r')

    def finalize(self):
        if self.state_path.exists():
            self.state_path.unlink()
        print(f"\n✅ Complete: {self.total} items in {(datetime.now(timezone.utc) - self.start_time).total_seconds():.1f}s")
PYEOF
 fi
python3 -m py_compile batch_resumer.py && echo "✅ batch_resumer.py OK"
# Retrofit foresight_collect.py with BatchResumer (idempotent)
python3 << 'PYEOF'
from pathlib import Path
content = Path('foresight_collect.py').read_text()
if 'from batch_resumer import BatchResumer' not in content:
    content = content.replace(
        'from collections import defaultdict, Counter',
        'from collections import defaultdict, Counter\nfrom batch_resumer import BatchResumer'
    )
    old_loop = '''    for f in staged_files:
        # Count direct + transitive dependents (BFS up to 3 hops)
        visited = set()
        queue = [(f, 0)]
        count = 0
        while queue:
            current, depth = queue.pop(0)
            if current in visited or depth > 3:
                continue
            visited.add(current)
            if current != f:
                count += 1
            for dep in reverse_graph.get(current, []):
                if dep not in visited:
                    queue.append((dep, depth + 1))
        impact_scores[f] = count'''
    new_loop = '''    state_file = MAP / 'foresight_impact_checkpoint.state'
    br = BatchResumer(state_file, len(staged_files), flush_every=50)
    for f, i, is_checkpoint in br.process(staged_files):
        visited = set()
        queue = [(f, 0)]
        count = 0
        while queue:
            current, depth = queue.pop(0)
            if current in visited or depth > 3:
                continue
            visited.add(current)
            if current != f:
                count += 1
            for dep in reverse_graph.get(current, []):
                if dep not in visited:
                    queue.append((dep, depth + 1))
        impact_scores[f] = count
        if is_checkpoint:
            br.checkpoint()
    br.finalize()'''
    if old_loop in content:
        content = content.replace(old_loop, new_loop)
        Path('foresight_collect.py').write_text(content)
        print("✅ foresight_collect.py retrofitted with BatchResumer")
    else:
        print("⚠️  Loop not found – may already be updated?")
else:
    print("ℹ️  BatchResumer already imported.")
PYEOF

python3 -m py_compile foresight_collect.py && echo "✅ foresight_collect.py OK"
cd ~/workspace/llm_map
# Quick check: did archaeologist complete? (look for finish line)
python3 archaeologist.py deepcli/deepcli/core.py --full 2>&1 | tail -5
# If it still shows only 1 event, correlation bridge needs a handshake.
# We can force‑feed the correlation with the known sessions from temporal_provenance.
# 1. Check what's actually in the correlation index (keys)
python3 -c "
import json
ci = json.load(open('$HOME/cli-synthegration/workspace/correlation/correlation_index.json'))
corrs = ci.get('correlations', {})
print(f'Correlation keys: {len(corrs)}')
for k in list(corrs.keys())[:10]:
    print(f'  {k}: {corrs[k]}')
"
# 2. Find any temporal entry that references 'core.py' or 'deepcli'
python3 -c "
import json
tp = json.load(open('$HOME/cli-synthegration/workspace/provenance/temporal_provenance.json'))
matches = [(k, v.get('session','')[:12]) for k, v in tp.items() if 'core.py' in k or 'deepcli' in k]
print(f'Temporal matches for core/deepcli: {len(matches)}')
for k, s in matches[:10]:
    print(f'  {k}  -> session {s}')
"
# 3. Check true_versions for deepcli/core.py
python3 -c "
import json
tv = json.load(open('$HOME/cli-synthegration/workspace/provenance/true_versions.json'))
matches = [(k, v) for k, v in tv.items() if 'deepcli' in k.lower() and 'core' in k.lower()]
print(f'True version matches: {len(matches)}')
for k, v in matches[:5]:
    print(f'  {k}: {v}')
"
synthegration
cd ~/workspace/llm_map
# 1. Export all DeepSeek sessions to create temporal blobs and provenance records
#    (This is the command that populates temporal_provenance.json and true_versions.json)
synthegration export-all
# 2. Rebuild the codex index (updates correlation_index.json with session‑to‑code mappings)
synthegration codex-index
# 3. Optionally, run categorization to group sessions by topic
synthegration categories
# 4. Re‑run the archaeologist after the data is populated
python3 archaeologist.py deepcli/deepcli/core.py --full
cd ~/workspace/llm_map
# 1. What does synthegration search find for core.py?
echo "=== synthegration search ==="
synthegration search "deepcli/core.py" 2>&1 | head -20
# 2. Check the raw temporal_provenance structure
echo ""
echo "=== Temporal provenance structure ==="
python3 -c "
import json
tp = json.load(open('$HOME/cli-synthegration/workspace/provenance/temporal_provenance.json'))
keys = list(tp.keys())
print(f'Total entries: {len(keys)}')
print(f'First 3 keys: {keys[:3]}')
if keys:
    print(f'First entry fields: {list(tp[keys[0]].keys())}')
    # Check if any entry has a 'source_file' or 'file' field
    for k in keys[:5]:
        fields = list(tp[k].keys()) if isinstance(tp[k], dict) else []
        print(f'  {k}: fields={fields}')
"
# 3. Check correlation index — does it map to sessions or just __pycache__?
echo ""
echo "=== Correlation entry types ==="
python3 -c "
import json
ci = json.load(open('$HOME/cli-synthegration/workspace/correlation/correlation_index.json'))
corrs = ci.get('correlations', {})
# Count how many values are session IDs vs file paths
sessions = 0
pycache = 0
for k, v in corrs.items():
    if isinstance(v, list):
        for item in v:
            if '__pycache__' in str(item):
                pycache += 1
            elif len(str(item)) > 30 and '-' in str(item):
                sessions += 1
print(f'Entries with session IDs: {sessions}')
print(f'Entries with __pycache__ refs: {pycache}')
print(f'Total keys: {len(corrs)}')
# Show one entry that has session-like values (UUID)
for k, v in corrs.items():
    if isinstance(v, list):
        for item in v:
            if len(str(item)) > 30 and '-' in str(item):
                print(f'  Session-key example: {k} -> {item}')
                break
"
# 4. Check if codex-index created new data
echo ""
echo "=== Codex index files ==="
find ~/cli-synthegration/codex -name "*.json" -newer ~/cli-synthegration/workspace/correlation/correlation_index.json 2>/dev/null | head -10
echo ""
ls -la ~/cli-synthegration/codex/*.json 2>/dev/null | head -5
# 5. How many sessions does synthegration sessions report?
echo ""
echo "=== Session count ==="
synthegration sessions 2>&1 | wc -l
# 6. Use our own router to find deepcli/core.py in the index
echo ""
echo "=== Router check ==="
python3 router_agent.py "deepcli core.py" 2>&1 | head -15
cd ~/workspace/llm_map
python3 -c "
import json
ci = json.load(open('$HOME/cli-synthegration/codex/codex_index.json'))
# Show structure
print(f'Type: {type(ci).__name__}')
if isinstance(ci, dict):
    print(f'Keys: {list(ci.keys())[:10]}')
    # If it has a 'pointers' or 'files' key, show sample
    for k in list(ci.keys())[:1]:
        val = ci[k]
        if isinstance(val, list) and len(val) > 0:
            print(f'  {k} is list of {len(val)} items; first: {json.dumps(val[0], indent=2)[:200]}')
        elif isinstance(val, dict):
            subkeys = list(val.keys())[:3]
            print(f'  {k} dict with keys: {subkeys}')
"
cd ~/workspace/llm_map
# 1. Count how many unique sessions are in the codex
jq '.pointers | map(.sid) | unique | length' ~/cli-synthegration/codex/codex_index.json
# 2. Show a sample pointer with its taxonomy path
jq '.pointers[0] | {sid: .sid[0:8], hash: .ch, path: (.path | join(" → "))}' ~/cli-synthegration/codex/codex_index.json
# 3. How many codex hashes match temporal provenance blobs?
python3 -c "
import json
codex = json.load(open('$HOME/cli-synthegration/codex/codex_index.json'))
tp = json.load(open('$HOME/cli-synthegration/workspace/provenance/temporal_provenance.json'))
ch_hashes = {p['ch'] for p in codex['pointers']}
tp_keys = {k.split('/')[-1].replace('.blob','') for k in tp}
matches = ch_hashes & tp_keys
print(f'Codex hashes: {len(ch_hashes)}, Temporal blobs: {len(tp_keys)}, Matches: {len(matches)}')
# Show one match
for m in list(matches)[:1]:
    for p in codex['pointers']:
        if p['ch'] == m:
            print(f'  {p[\"ch\"][:8]} → session {p[\"sid\"][:12]} → path: {\" → \".join(p[\"path\"][-3:])}')
"
# 4. Check if funcfind can see the codex index script that writes this
funcfind cli-synthegration/synthegration_index.py 2>/dev/null | grep -i 'codex\|pointer\|CodexIndex' | head -10
cd ~/workspace/llm_map
python3 << 'PYEOF'
import json
from pathlib import Path

HOME = Path.home()
ci_path = HOME / 'cli-synthegration/workspace/correlation/correlation_index.json'

with open(ci_path) as f:
    cdata = json.load(f)

corrs = cdata.get('correlations', {})
# Filter: keep only entries where key contains '/' and is not a Rust target path
clean = {}
rust_patterns = ['.fingerprint/', 'target/release/', 'target/debug/', '.cargo/', '.rs", '.d"', 'invoked.timestamp']

for k, v in corrs.items():
    # Skip Rust artifacts
    if any(p in k for p in rust_patterns):
        continue
    # Skip if key looks like a binary/hash without extension
    if '/' not in k or k.endswith('.d') or k.endswith('.o'):
        continue
    # Keep source files, codex entries, chronos exports
    clean[k] = v

cdata['correlations'] = clean
cdata['meta']['cleaned_at'] = __import__('datetime').datetime.now(timezone.utc).isoformat()
cdata['meta']['retained_keys'] = len(clean)

with open(ci_path, 'w') as f:
    json.dump(cdata, f, indent=2)

print(f"✅ Correlation index cleaned: {len(corrs)} → {len(clean)} keys retained")
# Show a sample of what remains
for k in list(clean.keys())[:10]:
    print(f"  {k}: {clean[k]}")
PYEOF

cd ~/workspace/llm_map
# ── 1. Fix & run the correlation index cleaner ──
python3 << 'PYEOF'
import json
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
ci_path = HOME / 'cli-synthegration/workspace/correlation/correlation_index.json'
with open(ci_path) as f:
    cdata = json.load(f)

corrs = cdata.get('correlations', {})
# Corrected list — no stray quote
rust_patterns = [
    '.fingerprint/', 'target/release/', 'target/debug/',
    '.cargo/', 'invoked.timestamp'
]
clean = {}
for k, v in corrs.items():
    if any(p in k for p in rust_patterns):
        continue
    if '/' not in k or k.endswith('.d') or k.endswith('.o'):
        continue
    clean[k] = v

cdata['correlations'] = clean
cdata['meta']['cleaned_at'] = datetime.now(timezone.utc).isoformat()
cdata['meta']['retained_keys'] = len(clean)

with open(ci_path, 'w') as f:
    json.dump(cdata, f, indent=2)
print(f'Correlation index: {len(corrs)} → {len(clean)} keys')
PYEOF

# ── 2. Real session‑to‑file bridge from codex + temporal ──
python3 << 'PYEOF'
import json
from pathlib import Path
from collections import defaultdict

HOME = Path.home()
codex = json.load(open(HOME / 'cli-synthegration/codex/codex_index.json'))
tp = json.load(open(HOME / 'cli-synthegration/workspace/provenance/temporal_provenance.json'))
ci = json.load(open(HOME / 'cli-synthegration/workspace/correlation/correlation_index.json'))

# Build hash → session map from codex
hash_to_session = {}
for p in codex['pointers']:
    hash_to_session[p['ch']] = {
        'sid': p['sid'],
        'path': p.get('path', []),
        'message_index': p.get('mi', 0),
        'block_index': p.get('bi', 0)
    }

# Build blob hash → temporal data map
blob_hash_to_temporal = {}
for blob_path, info in tp.items():
    blob_hash = blob_path.split('/')[-1].replace('.blob', '')
    blob_hash_to_temporal[blob_hash] = {
        'blob': blob_path,
        'session': info.get('session', ''),
        'timestamp': info.get('timestamp_utc', ''),
        'hash': info.get('hash', '')[:8],
        'snippet': info.get('snippet', '')[:80]
    }

# Merge: codex hash links to temporal blob
session_files = defaultdict(set)     # session → {source files}
file_sessions = defaultdict(set)     # source file → {sessions}
match_count = 0

for ch, codex_info in hash_to_session.items():
    if ch in blob_hash_to_temporal:
        match_count += 1
        sid = codex_info['sid']
        tmp = blob_hash_to_temporal[ch]
        # Use taxonomy path as potential source file hint
        taxonomy = ' → '.join(codex_info['path'][-3:]) if codex_info['path'] else 'unknown'
        session_files[sid].add(taxonomy)
        file_sessions[taxonomy].add(sid)

print(f'Merged {match_count} codex→temporal links')
print(f'Sessions with files: {len(session_files)}')
print(f'Unique taxonomy paths: {len(file_sessions)}')

# Inject session IDs into correlation index for matching source files
# Map taxonomy path fragments to actual source file keys in correlation index
corrs = ci.get('correlations', {})
new_links = 0
for source_file in corrs:
    file_name = source_file.split('/')[-1]
    for taxonomy, sessions in file_sessions.items():
        if file_name.lower() in taxonomy.lower():
            if isinstance(corrs[source_file], list):
                for s in sessions:
                    if s not in corrs[source_file]:
                        corrs[source_file].append(s)
                        new_links += 1
            else:
                corrs[source_file] = list(sessions)
                new_links += len(sessions)

ci['correlations'] = corrs
ci['meta']['session_links_added'] = new_links
ci['meta']['source'] = 'codex_temporal_bridge'
with open(HOME / 'cli-synthegration/workspace/correlation/correlation_index.json', 'w') as f:
    json.dump(ci, f, indent=2)
print(f'Added {new_links} session links to correlation index')

# Show a few examples
for source_file, sessions in list(corrs.items())[:5]:
    has_sid = [s for s in (sessions if isinstance(sessions, list) else [sessions]) if len(str(s)) > 30]
    if has_sid:
        print(f'  {source_file} → sessions: {[s[:12] for s in has_sid]}')
PYEOF

# ── 3. Re‑run archaeologist with bridged data ──
python3 archaeologist.py deepcli/deepcli/core.py --full
# ── 4. Impact Oracle with real verdicts ──
python3 impact_oracle.py deepcli/deepcli/core.py
cd ~/workspace/llm_map
python3 -c "
import json
from pathlib import Path
from collections import defaultdict
H = Path.home()
codex = json.load(open(H/'cli-synthegration/codex/codex_index.json'))
mi = json.load(open(H/'cli-synthegration/codex/message_index.json'))
ci_path = H/'cli-synthegration/workspace/correlation/correlation_index.json'
ci = json.load(open(ci_path))
corrs = ci.get('correlations', {})

# message_index.json structure: top-level keys are session IDs
session_keys = set(mi.keys())
print(f'Sessions in message_index: {len(session_keys)}')

# For each source file in correlation index, check if its filename appears in any session's messages
# Faster: build a set of all filenames mentioned in session message text
# message_index is huge; we'll sample 5 sessions to see the structure
for sid in list(session_keys)[:1]:
    val = mi[sid]
    print(f'Sample session {sid[:12]}: type={type(val).__name__}, keys={list(val.keys())[:3] if isinstance(val,dict) else str(val)[:100]}')
" 2>&1 | head -20
ls ~/
cat ~/central_mapper_v420.py 
ls ~/termux-multi-agent/
python3 ~/deepcli-tui/tui.py
exit
cd ~/workspace/llm_map
# Alias wasn't loaded – add it to this shell and run the remaining tasks
alias dispatch='python3 ~/workspace/llm_map/dispatch_task.py'
source ~/.zshrc 2>/dev/null || true
# Set minimized context for these research/build tasks (no full file loads needed)
export CONTEXT_MODE=minimized
# Dispatch the 9 pending tasks
for tid in arch-013 sync-002 extract-001 extract-002 error-extract-001 report-001 tui-005 util-001 dedup-001; do   dispatch "$tid";   sleep 5   # cooldown between tasks
done
exec zsh
