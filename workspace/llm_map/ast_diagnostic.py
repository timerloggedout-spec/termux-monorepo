import json, re
from pathlib import Path

MAP = Path('.')
INDEX = MAP / 'llm_index_compact.jsonl'
MAP_OUT = MAP / 'full_map_output.txt'

# All indexed paths
with open(INDEX) as f:
    indexed = {json.loads(l)['p'] for l in f}

# All file paths mentioned in the signature map
sig_paths = set()
sig_re = re.compile(r'^(.+?):\s*(def |async function |function |class )')
with open(MAP_OUT, errors='replace') as f:
    for line in f:
        m = sig_re.match(line.strip())
        if m:
            raw = m.group(1)
            # Normalise: remove leading ./ or absolute prefix
            if raw.startswith('./'):
                rel = raw[2:]
            elif raw.startswith(str(Path.home())):
                rel = str(Path(raw).relative_to(Path.home()))
            else:
                rel = raw
            sig_paths.add(rel)

print(f"Signature map unique files: {len(sig_paths)}")
print(f"Indexed files: {len(indexed)}")
print(f"Matching files: {len(sig_paths & indexed)}")

missing = sig_paths - indexed
if missing:
    print(f"\nFiles in signature map but NOT in index: {len(missing)}")
    for p in sorted(missing)[:10]:
        print(f"  {p}")
else:
    print("\nAll signature paths exist in the index → injection should match all of them")
