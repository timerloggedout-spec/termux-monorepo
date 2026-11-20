import os, json, re
from collections import defaultdict

HOME = os.path.expanduser("~")

# Load existing flow map (data_path -> list of source files)
flow = defaultdict(list)
with open(HOME + "/tmp/data_flow_map.txt") as f:
    current = None
    for line in f:
        line = line.rstrip()
        if line.startswith("=== ") and line.endswith(" ==="):
            current = line[4:-4].strip()
        elif line.startswith("  -> "):
            flow[current].append(line[4:].strip())

# Read/Write detection on whole file content
READ_PATTERNS = [
    r'json\.load\b', r'json\.loads\b',
    r'open\s*\([^)]*[\'\"][rR][\'\"]',
    r'\.read\b', r'read_text\b',
    r'\.schema\b', r'SELECT\b.*FROM',
]
WRITE_PATTERNS = [
    r'json\.dump\b', r'json\.dumps\b',
    r'open\s*\([^)]*[\'\"][waWA][\'\"]',
    r'\.write\b', r'write_text\b',
    r'INSERT\s+INTO', r'CREATE\s+TABLE',
]

def classify(content):
    is_r = any(re.search(p, content) for p in READ_PATTERNS)
    is_w = any(re.search(p, content) for p in WRITE_PATTERNS)
    if is_r and is_w: return "RW"
    if is_r: return "R"
    if is_w: return "W"
    return "?"

rw_map = {}  # data_path -> list of (source_file, flag)
total = len(flow)
print(f"Classifying references for {total} data files...")
for i, (dp, sources) in enumerate(sorted(flow.items())):
    if i % 500 == 0:
        print(f"  {i}/{total}")
    entries = []
    for src in sources:
        fp = os.path.join(HOME, src)
        if not os.path.isfile(fp):
            continue
        try:
            with open(fp, 'r', errors='ignore') as f:
                content = f.read(500000)  # read up to 500KB
        except:
            continue
        flag = classify(content)
        entries.append((src, flag))
    rw_map[dp] = entries

# Save
with open(HOME + "/tmp/rw_map_v2.json", "w") as f:
    json.dump(rw_map, f, indent=2)
print(f"Done. Classified {sum(len(v) for v in rw_map.values())} references.")
