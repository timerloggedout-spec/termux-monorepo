import os
import re
from pathlib import Path

ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

def clean_ansi(text):
    return ANSI_ESCAPE.sub('', text)

def main():
    metadata_dir = Path("/home/ubuntu/termux-monorepo/docs/evaluations/manus/session_metadata")
    if not metadata_dir.exists():
        print("Metadata directory not found.")
        return

    for f in metadata_dir.glob("*.json"):
        print(f"Cleaning {f.name}...")
        content = f.read_text()
        cleaned = clean_ansi(content)
        f.write_text(cleaned)
    print("Cleanup complete.")

if __name__ == "__main__":
    main()
