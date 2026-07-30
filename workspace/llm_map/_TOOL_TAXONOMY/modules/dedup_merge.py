import sys, json
seen = set()
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    t = json.loads(line)
    if t['name'] not in seen:
        seen.add(t['name'])
        print(json.dumps(t))
