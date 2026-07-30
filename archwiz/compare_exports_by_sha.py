import json, os, sys

HOME = os.path.expanduser("~")
index_path = HOME + "/central_index.jsonl"

# Load index: sha -> list of paths
sha_map = {}
with open(index_path) as f:
    for line in f:
        try:
            rec = json.loads(line)
            sha = rec.get("sha")
            path = rec.get("path")
            if sha and "synthegration_exports" in path:
                sha_map.setdefault(sha, []).append(path)
        except:
            pass

print(f"Total indexed export files: {len(sha_map)} unique SHA hashes")

# Now scan the other export dirs and check if their files' hashes match
for target in ["storage/downloads/synthegration_exports", "storage/downloads/synthegration_batch_export"]:
    target = os.path.join(HOME, target)
    if not os.path.isdir(target):
        continue
    matched = 0
    unmatched = 0
    for root, dirs, files in os.walk(target):
        for fn in files:
            fpath = os.path.join(root, fn)
            # We can't get hash from index without reading the file unless the index covers these paths.
            # But if the file path relative to HOME is in the index, we can compare.
            rel = os.path.relpath(fpath, HOME)
            # check if any sha corresponds to this rel
            found = False
            for sha, paths in sha_map.items():
                if rel in paths:
                    found = True
                    break
            if found:
                matched += 1
            else:
                unmatched += 1
    print(f"  {target}: {matched} matched, {unmatched} not in index")
