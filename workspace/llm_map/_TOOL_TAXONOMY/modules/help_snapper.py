import sys, json, os, subprocess
tools_file = sys.argv[1]
help_dir = sys.argv[2]
os.makedirs(help_dir, exist_ok=True)
with open(tools_file) as f:
    for line in f:
        obj = json.loads(line.strip())
        name = obj['name']
        path = obj.get('path', '')
        help_file = os.path.join(help_dir, f"{name}.txt")
        if os.path.exists(help_file): continue
        try:
            res = subprocess.run([path, '--help'], capture_output=True, text=True, timeout=2)
            if res.returncode == 0 and res.stdout:
                with open(help_file, 'w') as hf:
                    hf.write('\n'.join(res.stdout.splitlines()[:20]))
        except: pass
