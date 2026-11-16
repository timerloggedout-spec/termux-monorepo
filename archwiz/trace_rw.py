import os, re, json
from collections import defaultdict

HOME = os.path.expanduser("~")
SRC_DIRS = [
    "workspace", "cli-synthegration", "harmony_hub", "archwiz",
    "deepcli", "deepseek-cli", "termux-multi-agent", "synthegration-cli",
    "commingle-swarm", "_1-Projects",
]
EXCLUDE = {'.git','node_modules','__pycache__','.hermes','browser-data','Cache','GPUCache','chunks','.cache','storage','synthegration_exports','sandbox'}
SRC_EXTS = {'.py','.sh','.js','.ts','.rs'}
MAX_SIZE = 200_000  # skip files >200KB for speed

# Load list of data files
with open(HOME + "/tmp/data_files_list.txt") as f:
    data_paths = [line.strip() for line in f if line.strip()]

# Build a mapping: data_path -> list of (source_file, rw_flag)
rw_map = defaultdict(set)  # key: data_path, value: set of (source, flag)

# Simple indicators
READ_INDICATORS = [
    r'open\s*\(\s*[\'\"]',
    r'json\.load\s*\(',
    r'json\.loads\s*\(',
    r'read_text\s*\(',
    r'\.read\s*\(',
    r'cat\s+',
    r'less\s+',
    r'head\s+',
    r'tail\s+',
    r'source\s+',
    r'\.schema\s+',
    r'SELECT.*FROM',  # sqlite
]
WRITE_INDICATORS = [
    r'open\s*\(\s*[\'\"].*[\'\"]\s*,\s*[\'\"][wa][\'\"]',  # write/append mode
    r'json\.dump\s*\(',
    r'json\.dumps\s*\(',
    r'write_text\s*\(',
    r'\.write\s*\(',
    r'echo\s+.*>',  # shell write
    r'tee\s+',
    r'cp\s+',
    r'mv\s+',
    r'INSERT\s+INTO',  # sqlite
    r'CREATE\s+TABLE',
]

def analyze_file(src_path):
    """Returns list of (data_path, flag) found in this source file."""
    try:
        with open(src_path, 'r', errors='ignore') as f:
            content = f.read()
    except:
        return []
    results = []
    for dp in data_paths:
        # Check if the literal data path appears in this source
        if dp in content:
            # Determine flag by scanning the context around the occurrence
            # Simple: find the line containing the path
            idx = content.find(dp)
            if idx == -1:
                continue
            line_start = content.rfind('\n', 0, idx) + 1
            line_end = content.find('\n', idx)
            if line_end == -1:
                line_end = len(content)
            line = content[line_start:line_end]
            
            is_read = False
            is_write = False
            # Check for read indicators
            for pattern in READ_INDICATORS:
                if re.search(pattern, line, re.IGNORECASE):
                    is_read = True
                    break
            # Check for write indicators
            for pattern in WRITE_INDICATORS:
                if re.search(pattern, line, re.IGNORECASE):
                    is_write = True
                    break
            
            if is_read and is_write:
                flag = "RW"
            elif is_read:
                flag = "R"
            elif is_write:
                flag = "W"
            else:
                flag = "?"
            results.append((dp, flag))
    return results

# Walk source directories
src_files = []
for d in SRC_DIRS:
    dp = os.path.join(HOME, d)
    if not os.path.isdir(dp):
        continue
    for root, dirs, files in os.walk(dp, followlinks=False):
        dirs[:] = [d for d in dirs if d not in EXCLUDE and not d.startswith('.')]
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in SRC_EXTS:
                fp = os.path.join(root, f)
                try:
                    if os.path.getsize(fp) > MAX_SIZE:
                        continue
                except:
                    continue
                src_files.append(fp)

total = len(src_files)
print(f"Analyzing {total} source files for read/write patterns...")
for i, src in enumerate(src_files):
    if i % 200 == 0:
        print(f"  {i}/{total} {os.path.basename(src)}")
    for dp, flag in analyze_file(src):
        # store relative source path
        rel_src = os.path.relpath(src, HOME)
        rw_map[dp].add((rel_src, flag))

# Save raw results
out_path = HOME + "/tmp/rw_map.json"
serializable = {k: list(v) for k, v in rw_map.items()}
with open(out_path, 'w') as f:
    json.dump(serializable, f, indent=2)
print(f"Done. Found read/write info for {len(rw_map)} data files. Saved to tmp/rw_map.json")
