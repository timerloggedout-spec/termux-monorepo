import sys, json, os, datetime

top_file = sys.argv[1]
delta_dir = sys.argv[2]
os.makedirs(delta_dir, exist_ok=True)
now = datetime.datetime.now(datetime.timezone.utc).isoformat() + 'Z'
new_tools = []
if os.path.exists(top_file):
    with open(top_file) as f: data = json.load(f)
    prev_delta = os.path.join(delta_dir, "latest.json")
    if os.path.exists(prev_delta):
        with open(prev_delta) as f: prev = json.load(f)
        prev_set = set(t['name'] for t in prev.get('new_tools', []))
        curr_set = set(data.get('metadata', {}).get('all_tool_names', []))
        new_names = curr_set - prev_set
        new_tools = [{"name": n} for n in new_names]
    delta = {"timestamp": now, "new_tools": new_tools}
    with open(os.path.join(delta_dir, f"{now}.json"), 'w') as f: json.dump(delta, f, indent=2)
    try: os.remove(prev_delta)
    except: pass
    os.symlink(f"{now}.json", prev_delta)
    with open(os.path.join(os.path.dirname(delta_dir), "state", "last_run_time"), 'w') as f: f.write(now)
