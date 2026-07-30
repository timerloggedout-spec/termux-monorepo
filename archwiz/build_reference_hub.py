import os
from pathlib import Path
from datetime import datetime

HOME = Path.home()
DOCS = {
    "Data‑Flow Manifest": HOME / "archwiz/DATA_FLOW_MANIFEST.md",
    "Tool Index": HOME / "archwiz/TOOL_INDEX.md",
    "Caveman Index": HOME / "workspace/llm_map/CAVEMAN_INDEX.md",
    "System Map": HOME / "workspace/llm_map/SYSTEM_MAP.md",
    "Function Index": HOME / "workspace/llm_map/func_index.jsonl",
    "LLM Index Compact": HOME / "workspace/llm_map/llm_index_compact.jsonl",
    "RW Map": HOME / "tmp/rw_map_v2.json",
}

lines = ["# 📚 Reference Hub — Auto‑Generated", f"**Updated:** {datetime.now().isoformat()}", ""]
for name, path in DOCS.items():
    if path.exists():
        size = path.stat().st_size
        lines.append(f"- [{name}]({path}) ({size//1024} KB)")
    else:
        lines.append(f"- {name} — *missing*")

out = HOME / "archwiz/REFERENCE_HUB.md"
with open(out, "w") as f: f.write("\n".join(lines))
print(f"✅ {out}")
