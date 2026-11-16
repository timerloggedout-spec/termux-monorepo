python3 << 'PYEOF'
import json
from pathlib import Path

HOME = Path.home()
manifest = HOME / "storage/downloads/synthegration_exports/417ddd6d-9711-465d-ab90-c92cc04aeabf/manifest.json"
if manifest.exists():
    data = json.loads(manifest.read_text())
    for b in data:
        if not isinstance(b, dict): continue
        code = b.get("code", "")
        if "Build commit-notes tool" in code or "Router Agent: scans session logs" in code:
            print("FOUND in current session manifest!")
            print(b.get("code", "")[:1000])
            break
    else:
        print("Not found in current session manifest.")
else:
    print("Current session manifest not found.")
PYEOF