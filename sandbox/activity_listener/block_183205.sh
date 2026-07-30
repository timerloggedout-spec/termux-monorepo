python3 << 'PYEOF'
import sys, json
from pathlib import Path

HOME = Path.home()
sys.path.insert(0, str(HOME / 'cli-synthegration'))
from synthegration_index import CodexIndex

# The original class needs a base_dir; use the existing codex directory
codex_dir = HOME / 'cli-synthegration' / 'codex'
idx = CodexIndex(codex_dir)

# Search for the send_message function body across all exports
results = idx.find_similar_blocks(
    "def send_message(token: str, session_id: str, prompt: str",
    min_similarity=0.6
)

print(f"Found {len(results)} matching blocks.\n")
for i, (pointer, score, snippet) in enumerate(results[:10]):
    print(f"--- Match {i} (score {score:.2f}) ---")
    print(f"Session: {pointer.session_id}")
    print(f"Message: {pointer.msg_idx}, Block: {pointer.blk_idx}")
    print(f"Code:\n{snippet[:300]}")
    print()
PYEOF