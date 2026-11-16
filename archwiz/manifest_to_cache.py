#!/usr/bin/env python3
"""Convert synthegration manifest.json → TUI cache messages array."""
import json, sys
from pathlib import Path

manifest_path = Path(sys.argv[1])
cache_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.home() / '.deepcli/session_store' / f'{manifest_path.parent.name}.json'

data = json.loads(manifest_path.read_text())
messages = []
for entry in data:
    raw = entry.get('code', '')
    if not raw.strip():
        continue
    lang = entry.get('language', 'text')
    if lang != 'text':
        content = f"```{lang}
{raw}
```"
    else:
        content = raw
    role = entry.get('message_role', 'USER').lower()
    # Synthegration uses uppercase roles; TUI cache expects lowercase
    messages.append({
        'message_id': entry.get('code_hash', ''),
        'role': role if role in ('user','assistant') else 'user',
        'content': content,
        'timestamp': entry.get('message_timestamp', ''),
    })

cache_path.parent.mkdir(parents=True, exist_ok=True)
cache_path.write_text(json.dumps(messages))
print(f'{len(messages)} messages written to {cache_path}')
