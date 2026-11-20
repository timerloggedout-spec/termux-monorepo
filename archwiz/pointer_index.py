#!/usr/bin/env python3
"""Pointer Index – resolve code hashes to their source in exports without copying."""
import json
import sys
from pathlib import Path

HOME = Path.home()
EXPORTS_DIR = HOME / 'synthegration_exports'
INDEX_FILE = HOME / 'archwiz/pointer_index.json'

def build_index():
    """Build a hash → location map from all exported manifests."""
    index = {}
    for d in EXPORTS_DIR.iterdir():
        if not d.is_dir(): continue
        m = d / 'manifest.json'
        sf = d / 'session.json'
        if m.exists():
            try:
                blocks = json.loads(m.read_text())
            except:
                continue
            if not isinstance(blocks, list):
                continue
            for i, b in enumerate(blocks):
                if not isinstance(b, dict):
                    continue
                h = b.get('code_hash', '').strip()
                if h:
                    index[h] = {'session_id': d.name, 'manifest_index': i}
        elif sf.exists():
            try:
                data = json.loads(sf.read_text())
            except:
                continue
            msgs = data if isinstance(data, list) else data.get('messages', [])
            block_idx = 0
            import re as _re
            import hashlib as _hl
            for msg in msgs:
                if not isinstance(msg, dict):
                    continue
                content = msg.get('content', '')
                for match in _re.finditer(r"""```(\w+)?\n(.*?)```""", content, _re.DOTALL):
                    code_text = match.group(2)
                    h = _hl.sha256(code_text.encode()).hexdigest()[:16]
                    if h not in index:
                        index[h] = {'session_id': d.name, 'manifest_index': block_idx}
                    block_idx += 1
        else:
            continue

    INDEX_FILE.write_text(json.dumps(index, indent=2))
    print(f"Index built: {len(index)} code blocks mapped.")
    return index

def load_index():
    if INDEX_FILE.exists():
        return json.loads(INDEX_FILE.read_text())
    return build_index()

def resolve(hash_or_pointer, show=True):
    """Retrieve a code block by hash or CID pointer (→xxxx)."""
    ptr = hash_or_pointer.lstrip('→')
    index = load_index()
    if ptr not in index:
        print(f"Pointer '{ptr}' not found in index.")
        return None
    loc = index[ptr]
    manifest = EXPORTS_DIR / loc['session_id'] / 'manifest.json'
    blocks = json.loads(manifest.read_text())
    block = blocks[loc['manifest_index']]
    code = block.get('code', '')
    if show:
        print(f"Session: {loc['session_id'][:32]}...")
        print(f"Role: {block.get('message_role','?')}")
        print(f"Timestamp: {block.get('message_timestamp','?')}")
        print(f"\n{code[:3000]}")
    return code

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: pointer_index.py build | resolve <hash>")
        sys.exit(1)
    if sys.argv[1] == 'build':
        build_index()
    elif sys.argv[1] == 'resolve' and len(sys.argv) > 2:
        resolve(sys.argv[2])
    else:
        print("Usage: pointer_index.py build | resolve <hash>")
