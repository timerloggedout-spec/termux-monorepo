#!/usr/bin/env python3
"""Chronos: time‑travel through conversation history.
Usage:
  chronos.py list <session_id> [--every N] [--role USER|ASSISTANT]
  chronos.py checkout <session_id> <message_id> [--output-dir <dir>]
  chronos.py diff <session_id> <msg_a> <msg_b>
  chronos.py blob <hash_prefix>
  chronos.py branch-tree <session_id>
"""
import sys, re, json, hashlib
from pathlib import Path
from typing import Optional, List, Dict, Any

HOME = Path.home()
sys.path.insert(0, str(HOME / 'deepcli'))
from deepcli.core import get_token, get_history

class ChronosSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.token = get_token()
        self._messages: List[Dict[str, Any]] = []
        self._loaded = False

    def _load(self):
        if not self._loaded:
            self._messages = get_history(self.token, self.session_id)
            self._loaded = True

    @property
    def messages(self) -> List[Dict[str, Any]]:
        self._load()
        return self._messages

    def list_versions(self, every: int = 50, role_filter: str = None):
        """Print version checkpoints (every Nth message)."""
        msgs = self.messages
        print(f"Session {self.session_id}: {len(msgs)} messages")
        for i, m in enumerate(msgs):
            if role_filter and m.get('role', '') != role_filter:
                continue
            if i % every == 0 or i < 5 or i > len(msgs) - 3:
                content = (m.get('content', '') or '')[:80].replace('\n', ' ')
                msg_id = m.get('message_id', '?')
                parent = m.get('parent_id', '?')
                print(f"  v{i:03d} msg_id={msg_id} parent={parent} [{m.get('role','?')}] {content}...")

    def get_message(self, message_id: str) -> Optional[Dict[str, Any]]:
        for m in self.messages:
            if str(m.get('message_id')) == str(message_id):
                return m
        return None

    def checkout(self, message_id: str, output_dir: str = None):
        """Reconstruct all code blocks from a specific message into files."""
        msg = self.get_message(message_id)
        if not msg:
            print(f"Message {message_id} not found")
            return
        content = msg.get('content', '')
        blocks = re.findall(r'```(\w*)\n(.*?)```', content, re.DOTALL)
        if not blocks:
            print(f"No code blocks in message {message_id}")
            return
        out = Path(output_dir) if output_dir else HOME / 'chronos_checkout' / f'msg_{message_id}'
        out.mkdir(parents=True, exist_ok=True)
        for i, (lang, code) in enumerate(blocks):
            lang = lang or 'text'
            h = hashlib.sha256(code.encode()).hexdigest()[:12]
            ext = {'python':'py','javascript':'js','typescript':'ts','bash':'sh','rust':'rs','html':'html','css':'css','json':'json','yaml':'yaml','markdown':'md'}.get(lang, 'txt')
            fname = f"{i:02d}_{lang}_{h}.{ext}"
            (out / fname).write_text(code)
            print(f"  [{lang}] {fname}  ({len(code)} bytes, hash={h})")
        print(f"\nChecked out {len(blocks)} blocks to {out}")

    def diff(self, msg_a: str, msg_b: str):
        """Show what changed between two messages (code block hashes)."""
        a = self.get_message(msg_a)
        b = self.get_message(msg_b)
        if not a or not b:
            print("Message not found")
            return
        def extract_hashes(msg):
            blocks = re.findall(r'```(\w*)\n(.*?)```', msg.get('content',''), re.DOTALL)
            return {hashlib.sha256(code.encode()).hexdigest()[:12]: (lang, code[:80]) for lang, code in blocks}
        hashes_a = extract_hashes(a)
        hashes_b = extract_hashes(b)
        added = set(hashes_b) - set(hashes_a)
        removed = set(hashes_a) - set(hashes_b)
        unchanged = set(hashes_a) & set(hashes_b)
        print(f"Diff: msg {msg_a} → msg {msg_b}")
        print(f"  +{len(added)} added  -{len(removed)} removed  ={len(unchanged)} unchanged")
        for h in added:
            lang, snippet = hashes_b[h]
            print(f"  + [{lang}] {h}  {snippet}...")
        for h in removed:
            lang, snippet = hashes_a[h]
            print(f"  - [{lang}] {h}  {snippet}...")

    def branch_tree(self):
        """Display the conversation's branching structure."""
        msgs = self.messages
        # Build parent -> children map
        tree: Dict[str, List[str]] = {}
        for m in msgs:
            pid = str(m.get('parent_id', '')) or 'root'
            mid = str(m.get('message_id', ''))
            tree.setdefault(pid, []).append(mid)
        # Find forks (parents with >1 child)
        forks = {p: children for p, children in tree.items() if len(children) > 1}
        print(f"Session {self.session_id}: {len(msgs)} messages, {len(forks)} fork points")
        for parent, children in sorted(forks.items()):
            print(f"  Fork at msg {parent}: {len(children)} branches → {', '.join(children[:5])}")

    @staticmethod
    def blob_lookup(hash_prefix: str):
        """Search the codex blob store AND export manifests for a block by hash prefix."""
        found = []
        # 1. Search codex blobs
        blob_dir = HOME / 'cli-synthegration' / 'codex' / 'blobs'
        if blob_dir.exists():
            for f in blob_dir.glob(f"{hash_prefix}*"):
                found.append(('codex blob', f.stem, f.read_text()))
        # 2. Search export manifests
        exports_dir = HOME / 'synthegration_exports'
        if exports_dir.exists():
            for session_dir in exports_dir.iterdir():
                manifest = session_dir / 'manifest.json'
                if not manifest.exists(): continue
                try:
                    blocks = json.loads(manifest.read_text())
                except: continue
                if isinstance(blocks, list):
                    for b in blocks:
                        if isinstance(b, dict):
                            h = b.get('code_hash') or b.get('hash','')
                            if h and (h.startswith(hash_prefix) or hash_prefix.startswith(h)):
                                code = b.get('code_snippet') or b.get('code', '')
                                found.append(('export', h, code[:200]))
        if not found:
            print(f"No blob matches prefix '{hash_prefix}'")
            return
        for source, h, content in found[:5]:
            print(f"  [{source}] {h}  ({len(content)} bytes)")
            print(f"    {content[:200]}...")
            print()

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd = sys.argv[1]
    if cmd == 'list':
        sid = sys.argv[2] if len(sys.argv) > 2 else 'e102d768-8a47-4001-95cb-14fb6245c6fa'
        every = int(sys.argv[sys.argv.index('--every')+1]) if '--every' in sys.argv else 50
        role = sys.argv[sys.argv.index('--role')+1] if '--role' in sys.argv else None
        ChronosSession(sid).list_versions(every=every, role_filter=role)
    elif cmd == 'checkout':
        sid, mid = sys.argv[2], sys.argv[3]
        out_dir = sys.argv[sys.argv.index('--output-dir')+1] if '--output-dir' in sys.argv else None
        ChronosSession(sid).checkout(mid, out_dir)
    elif cmd == 'diff':
        sid, a, b = sys.argv[2], sys.argv[3], sys.argv[4]
        ChronosSession(sid).diff(a, b)
    elif cmd == 'blob':
        ChronosSession.blob_lookup(sys.argv[2])
    elif cmd == 'branch-tree':
        sid = sys.argv[2] if len(sys.argv) > 2 else 'e102d768-8a47-4001-95cb-14fb6245c6fa'
        ChronosSession(sid).branch_tree()
    else:
        print(f"Unknown command: {cmd}")

if __name__ == '__main__':
    main()
