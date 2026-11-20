import json, os, hashlib, sys

HOME = os.path.expanduser("~")
true_versions = json.load(open(os.path.join(HOME, "true_versions.json")))
# Build hash -> list of entries
hash_map = {}
for path, entries in true_versions.items():
    for e in entries:
        h = e.get("hash")
        if h:
            hash_map.setdefault(h, []).append({"path": path, "session": e["session"], "node": e["node_id"]})

target_dir = os.path.join(HOME, "storage/downloads/synthegration_exports")
if not os.path.isdir(target_dir):
    print("Target dir not found")
    sys.exit(1)

for root, dirs, files in os.walk(target_dir):
    for f in files:
        fpath = os.path.join(root, f)
        with open(fpath, "rb") as fh:
            h = hashlib.sha256(fh.read()).hexdigest()[:12]  # adjust to match your hash length
        if h in hash_map:
            print(f"MATCH (hash {h}): {fpath}")
            for ref in hash_map[h]:
                print(f"  → {ref['path']}  (session {ref['session']}, node {ref['node']})")
