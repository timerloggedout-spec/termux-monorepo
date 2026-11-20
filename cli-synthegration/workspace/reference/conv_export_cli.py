# CLI to extract & search conversation sessions
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path("/data/data/com.termux/files/home/deepseek_harvest_work/harvest.py").parent))
import harvest

def main():
    if len(sys.argv) < 2:
        print("Usage: conv_export_cli.py <search_term> [--export]")
        return
    term = sys.argv[1]
    results = harvest.search_conversations(term)  # adjust to actual function name
    if "--export" in sys.argv:
        out = Path.home() / "storage" / "downloads" / "synthegration_export.json"
        out.write_text(json.dumps(results, indent=2))
        print(f"Exported to {out}")
    else:
        print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
