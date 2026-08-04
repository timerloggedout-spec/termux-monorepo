#!/usr/bin/env python3
"""Content‑addressed hierarchical index with pointer references for minimal sync."""
import json
import hashlib
import re
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, timezone

class Pointer:
    """C++‑style lightweight reference: (session_id, msg_idx, blk_idx) -> content_hash."""
    __slots__ = ('session_id', 'message_index', 'block_index', 'content_hash', 'start_line', 'end_line')

    def __init__(self, session_id: str, msg_idx: int, blk_idx: int, content_hash: str, start_line: int = 0, end_line: int = 0):
        self.session_id = session_id
        self.message_index = msg_idx
        self.block_index = blk_idx
        self.content_hash = content_hash
        self.start_line = start_line
        self.end_line = end_line

    def to_key(self) -> str:
        return ""

    def citation(self) -> str:
        return ""
        """Return 【cursor_id†Lstart-Lend】 formatted citation."""
        cursor_id = f"{self.session_id[:8]}:{self.message_index}:{self.block_index}"
        if self.end_line > self.start_line:
            return f"【{cursor_id}†L{self.start_line}-L{self.end_line}】"
        return f"【{cursor_id}†L{self.start_line}】"

        return f"{self.session_id}:{self.message_index}:{self.block_index}"

    def to_wire(self) -> bytes:
        """Ultra‑compact binary representation (20 bytes + 8 byte hash)."""
        import struct
        sid_bytes = self.session_id.encode()[:12].ljust(12, b'\x00')
        packed = struct.pack('>12sII', sid_bytes, self.message_index, self.block_index)
        return packed + bytes.fromhex(self.content_hash)

    @classmethod
    def from_wire(cls, data: bytes) -> 'Pointer':
        import struct
        sid_bytes, msg_idx, blk_idx = struct.unpack('>12sII', data[:20])
        content_hash = data[20:28].hex()
        return cls(sid_bytes.rstrip(b'\x00').decode(), msg_idx, blk_idx, content_hash)

class _TaxonomyNode_v1:
    """Hierarchical taxonomy: language → project → session → timestamp."""
    __slots__ = ('name', 'children', 'pointers', 'meta')
    
    def __init__(self, name: str):
        self.name = name
        self.children: Dict[str, 'TaxonomyNode'] = {}
        self.pointers: List[Pointer] = []
        self.meta: Dict[str, Any] = {}
    
    def add_pointer(self, pointer: Pointer, path: List[str]):
        """Insert pointer along a hierarchical path, creating nodes as needed."""
        node = self
        for part in path:
            if part not in node.children:
                node.children[part] = TaxonomyNode(part)
            node = node.children[part]
        node.pointers.append(pointer)
    
    def search(self, term: str) -> List[Pointer]:
        """Recursive search by name or metadata."""
        results = []
        if term.lower() in self.name.lower():
            results.extend(self.pointers)
        for child in self.children.values():
            results.extend(child.search(term))
        return results
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'meta': self.meta,
            'pointers': [p.to_key() for p in self.pointers],
            'children': {k: v.to_dict() for k, v in self.children.items()}
        }

class _CodexIndex_v1:
    @staticmethod
    def from_live_exports(exports_root: str = None):
        """Build codex from all live-exported session manifests."""
        from pathlib import Path
        if exports_root is None:
            exports_root = Path.home() / "storage" / "downloads" / "synthegration_exports"
        exports_root = Path(exports_root)
        if not exports_root.exists():
            return CodexIndex()
        all_blocks = []
        for session_dir in exports_root.iterdir():
            manifest = session_dir / "manifest.json"
            if manifest.exists():
                blocks = json.loads(manifest.read_text())
                for b in blocks:
                    b["session_id"] = session_dir.name
                all_blocks.extend(blocks)
        idx = CodexIndex(Path.home() / "cli-synthegration" / "codex")
        idx._ingest_blocks(all_blocks)
        return idx

    @staticmethod

    def __init__(self, session_id: str, msg_idx: int, blk_idx: int, content_hash: str, start_line: int = 0, end_line: int = 0):
        self.session_id = session_id
        self.message_index = msg_idx
        self.block_index = blk_idx
        self.content_hash = content_hash
        self.start_line = start_line
        self.end_line = end_line

    def to_key(self) -> str:
        return ""

    def citation(self) -> str:
        return ""
        """Return 【cursor_id†Lstart-Lend】 formatted citation."""
        cursor_id = f"{self.session_id[:8]}:{self.message_index}:{self.block_index}"
        if self.end_line > self.start_line:
            return f"【{cursor_id}†L{self.start_line}-L{self.end_line}】"
        return f"【{cursor_id}†L{self.start_line}】"

        return f"{self.session_id}:{self.message_index}:{self.block_index}"

    def to_wire(self) -> bytes:
        """Ultra‑compact binary representation (20 bytes + hash)."""
        import struct
        sid_bytes = self.session_id.encode()[:12].ljust(12, b'\x00')
        packed = struct.pack('>12sII', sid_bytes, self.message_index, self.block_index)
        return packed + bytes.fromhex(self.content_hash)

    @classmethod
    def from_wire(cls, data: bytes) -> 'Pointer':
        import struct
        sid_bytes, msg_idx, blk_idx = struct.unpack('>12sII', data[:20])
        content_hash = data[20:28].hex()
        return cls(sid_bytes.rstrip(b'\x00').decode(), msg_idx, blk_idx, content_hash)

class TaxonomyNode:
    """Hierarchical taxonomy: language → project → session → timestamp."""
    __slots__ = ('name', 'children', 'pointers', 'meta')
    
    def __init__(self, name: str):
        self.name = name
        self.children: Dict[str, 'TaxonomyNode'] = {}
        self.pointers: List[Pointer] = []
        self.meta: Dict[str, Any] = {}
    
    def add_pointer(self, pointer: Pointer, path: List[str]):
        """Insert pointer along a hierarchical path, creating nodes as needed."""
        node = self
        for part in path:
            if part not in node.children:
                node.children[part] = TaxonomyNode(part)
            node = node.children[part]
        node.pointers.append(pointer)
    
    def search(self, term: str) -> List[Pointer]:
        """Recursive search by name or metadata."""
        results = []
        if term.lower() in self.name.lower():
            results.extend(self.pointers)
        for child in self.children.values():
            results.extend(child.search(term))
        return results
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'meta': self.meta,
            'pointers': [p.to_key() for p in self.pointers],
            'children': {k: v.to_dict() for k, v in self.children.items()}
        }

class CodexIndex:
    @staticmethod
    def from_live_exports(exports_root: str = None):
        """Build codex from live-exported session manifests (manifest.json or session.json)."""
        from pathlib import Path
        if exports_root is None:
            exports_root = Path.home() / "synthegration_exports"
        exports_root = Path(exports_root)
        if not exports_root.exists():
            return CodexIndex()
        all_blocks = []
        for session_dir in exports_root.iterdir():
            manifest = session_dir / "manifest.json"
            session_file = session_dir / "session.json"
            if manifest.exists():
                blocks = json.loads(manifest.read_text())
                for b in blocks:
                    b["session_id"] = session_dir.name
                all_blocks.extend(blocks)
            elif session_file.exists():
                data = json.loads(session_file.read_text())
                msgs = data if isinstance(data, list) else data.get("messages", data.get("chat_messages", []))
                for mi, msg in enumerate(msgs):
                    if not isinstance(msg, dict):
                        continue
                    content = msg.get("content", "")
                    for bi, match in enumerate(__import__("re").finditer(r"```(\w+)?\n(.*?)```", content, __import__("re").DOTALL)):
                        lang = (match.group(1) or "text").lower()
                        code_text = match.group(2)
                        ch = __import__("hashlib").sha256(code_text.encode()).hexdigest()[:16]
                        all_blocks.append({
                            "session_id": session_dir.name,
                            "mi": mi, "bi": bi, "ch": ch,
                            "path": [lang, session_dir.name[:8]],
                            "code": code_text
                        })
        idx = CodexIndex(Path.home() / "cli-synthegration" / "codex")
        idx._ingest_blocks(all_blocks)
        return idx

    def _ingest_blocks(self, blocks: list):
        """Add a list of code blocks to the codex."""
        import hashlib
        for blk in blocks:
            sid = blk.get("session_id", "unknown")
            mi = blk.get("mi", blk.get("message_index", 0))
            bi = blk.get("bi", blk.get("block_index", 0))
            ch = blk.get("ch", blk.get("content_hash", ""))
            if not ch:
                code_text = blk.get("code", "")
                if code_text:
                    ch = hashlib.sha256(code_text.encode()).hexdigest()[:16]
            if not ch:
                continue
            path = blk.get("path", ["uncategorized"])
            p = Pointer(sid, mi, bi, ch)
            self.taxonomy.add_pointer(p, path)
            # root pointers handled via add_pointer
            self.blobs[ch] = blk.get("code", "")
            ts = blk.get("ts")
            if ts:
                try:
                    self.time_index[ch] = datetime.fromisoformat(ts)
                except Exception:
                    pass

    @staticmethod
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path.home() / 'cli-synthegration' / 'codex'
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.taxonomy = TaxonomyNode("root")
        self.blobs: Dict[str, str] = {}            # content_hash → file_path
        self.time_index: Dict[str, datetime] = {}   # content_hash → timestamp
        self.version_history: Dict[str, List[str]] = {}
        self.hash_to_pointer: Dict[str, Pointer] = {}  # content_hash → Pointer for reverse lookup
        self._load()
        self._rebuild_hash_index()
    
    def _load(self):
        index_file = self.base_dir / 'codex_index.json'
        if index_file.exists():
            data = json.loads(index_file.read_text())
            self._from_flat(data)
    
    def _from_flat(self, data: dict):
        for ptr_data in data.get('pointers', []):
            p = Pointer(ptr_data['sid'], ptr_data['mi'], ptr_data['bi'], ptr_data['ch'])
            path = ptr_data.get('path', ['uncategorized'])
            self.taxonomy.add_pointer(p, path)
            ts = ptr_data.get('ts')
            if ts:
                self.time_index[p.content_hash] = datetime.fromisoformat(ts)
    
    
    def _rebuild_hash_index(self):
        """Rebuild blobs dict and hash→pointer by scanning disk."""
        blob_dir = self.base_dir / "blobs"
        if not blob_dir.exists():
            return
        for blob_file in blob_dir.glob("*.blob"):
            ch = blob_file.stem
            self.blobs[ch] = str(blob_file)
            if ch not in self.hash_to_pointer:
                self.hash_to_pointer[ch] = Pointer("imported", 0, 0, ch)
    def _save(self):
        flat = {'pointers': [], 'version': 1}
        def flatten(node, path):
            for p in node.pointers:
                flat['pointers'].append({
                    'sid': p.session_id, 'mi': p.message_index, 'bi': p.block_index,
                    'ch': p.content_hash, 'path': path,
                    'ts': self.time_index.get(p.content_hash, datetime.now(timezone.utc)).isoformat()
                })
            for name, child in node.children.items():
                flatten(child, path + [name])
        flatten(self.taxonomy, ['root'])
        (self.base_dir / 'codex_index.json').write_text(json.dumps(flat, indent=2))
    
    def index_conversation(self, session_id: str, title: str, messages: List[dict],
                           language_detect: bool = True):
        """Index all code blocks from a conversation into the taxonomy."""
        project = self._safe_name(title)
        for msg_idx, msg in enumerate(messages):
            content = msg.get('content', '')
            role = msg.get('role', 'unknown')
            ts = msg.get('inserted_at', msg.get('timestamp', ''))
            for blk_idx, match in enumerate(re.finditer(r"```(\w+)?\n(.*?)```", content, re.DOTALL)):
                lang = (match.group(1) or 'text').lower()
                code = match.group(2)
                ch = hashlib.sha256(code.encode()).hexdigest()[:16]
                p = Pointer(session_id, msg_idx, blk_idx, ch)
                path = [lang, project, role]
                self.taxonomy.add_pointer(p, path)
                self.time_index[ch] = datetime.fromisoformat(ts) if ts else datetime.now(timezone.utc)
                # Store blob if not already
                blob_path = self.base_dir / 'blobs' / f"{ch}.blob"
                blob_path.parent.mkdir(exist_ok=True)
                if not blob_path.exists():
                    blob_path.write_text(code)
                self.blobs[ch] = str(blob_path)
                self.hash_to_pointer[ch] = p
        self._save()
    
    def compute_diff(self, other_index_file: Path) -> List[Pointer]:
        """Return pointers present in other but missing locally (minimal sync)."""
        other = CodexIndex(other_index_file.parent)
        local_hashes = set(self.blobs.keys())
        remote_hashes = set(other.blobs.keys())
        missing = remote_hashes - local_hashes
        return [p for p_list in [other.taxonomy.search(h) for h in missing] for p in p_list]
    
    def sync_wire_format(self, pointers: List[Pointer]) -> bytes:
        """Compact binary representation for network transfer."""
        return b''.join(p.to_wire() for p in pointers)
    
    def search_by_taxonomy(self, term: str, lang: str = None, project: str = None) -> List[dict]:
        """Search with optional taxonomy filters."""
        results = []
        for p in self.taxonomy.search(term):
            if lang and not any(lang in part for part in [p.session_id, '']):
                continue  # simplistic
            blob = self.base_dir / 'blobs' / f"{p.content_hash}.blob"
            if blob.exists():
                results.append({
                    'pointer': p.to_key(),
                    'hash': p.content_hash,
                    'code': blob.read_text()[:200] + '...' if len(blob.read_text()) > 200 else blob.read_text(),
                    'timestamp': self.time_index.get(p.content_hash, '').isoformat()
                })
        return results
    
    @staticmethod
    def _safe_name(name: str) -> str:
        return re.sub(r'[\\/*?:"<>|\[\]]', '_', name)[:60]


    # ----- Similarity chunking -----
    def chunk_similarity(self, min_similarity: float = 0.7):
        """Group code blocks by content similarity using MinHash."""
        try:
            from datasketch import MinHash, MinHashLSH
        except ImportError:
            # Fallback: use simple token overlap
            return self._simple_similarity(min_similarity)

        lsh = MinHashLSH(threshold=min_similarity, num_perm=128)
        chunks = []
        for ch, blob_path in self.blobs.items():
            if not Path(blob_path).exists():
                continue
            code = Path(blob_path).read_text()
            m = MinHash(num_perm=128)
            for token in code.split():
                m.update(token.encode('utf8'))
            lsh.insert(ch, m)
            chunks.append((ch, code))

        clusters = {}
        for ch, code in chunks:
            neighbors = lsh.query(lsh.keys[ch] if hasattr(lsh,'keys') else lsh._keys.get(ch, None))
            if neighbors:
                canonical = min(neighbors)
                clusters.setdefault(canonical, []).append((ch, code[:100]))
        return clusters

    def _simple_similarity(self, min_similarity: float = 0.7):
        """Fallback: token overlap similarity for code blocks."""
        from difflib import SequenceMatcher
        items = []
        for ch, blob_path in self.blobs.items():
            if Path(blob_path).exists():
                items.append((ch, Path(blob_path).read_text()[:500]))
        clusters = {}
        used = set()
        for i, (ch1, code1) in enumerate(items):
            if ch1 in used:
                continue
            cluster = [(ch1, code1[:80])]
            used.add(ch1)
            for j, (ch2, code2) in enumerate(items):
                if ch2 in used:
                    continue
                if SequenceMatcher(None, code1, code2).ratio() >= min_similarity:
                    cluster.append((ch2, code2[:80]))
                    used.add(ch2)
            if len(cluster) > 1:
                clusters[ch1] = cluster
        return clusters

    def fuzzy_clusters(self, min_shared_phrases: int = 5) -> list:
        """Use existing inverted message index to find code blocks that share rare phrases."""
        # Load message index
        mi = MessageIndex.load(self.base_dir)
        if not mi.inverted:
            return []
        # Build code-to-phrases map
        code_phrases = {}
        for ch, blob_path in self.blobs.items():
            if not Path(blob_path).exists():
                continue
            code = Path(blob_path).read_text()[:2000]  # first 2k chars
            # Extract 3-5 word phrases
            words = __import__('re').findall(r'\w+', code)
            phrases = set()
            for i in range(len(words)-2):
                phrases.add(' '.join(words[i:i+3]))
            code_phrases[ch] = phrases
        # For each code, find others with overlapping phrases
        clusters = {}
        hashes = list(code_phrases.keys())
        for i in range(len(hashes)):
            ch1 = hashes[i]
            phrases1 = code_phrases[ch1]
            for j in range(i+1, len(hashes)):
                ch2 = hashes[j]
                phrases2 = code_phrases[ch2]
                overlap = phrases1 & phrases2
                if len(overlap) >= min_shared_phrases:
                    canonical = min(ch1, ch2)
                    clusters.setdefault(canonical, []).append(ch2 if canonical == ch1 else ch1)
        return clusters

    def find_similar_blocks(self, code: str, min_similarity: float = 0.6) -> list:
        """Find existing blocks similar to the given code."""
        from difflib import SequenceMatcher
        results = []
        for ch, blob_path in self.blobs.items():
            if not Path(blob_path).exists():
                continue
            existing = Path(blob_path).read_text()
            ratio = SequenceMatcher(None, code[:1000], existing[:1000]).ratio()
            if ratio >= min_similarity:
                results.append((ch, ratio, existing[:200]))
        return sorted(results, key=lambda x: -x[1])[:20]

if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path.home() / 'deepcli'))
    from deepcli.core import get_token, fetch_sessions, get_history
    
    idx = CodexIndex(Path.home() / "cli-synthegration" / "codex")
    token = get_token()
    sessions = fetch_sessions(token)[:20]  # index first 20
    for s in sessions:
        msgs = get_history(token, s['id'])
        if msgs:
            idx.index_conversation(s['id'], s.get('title', 'Untitled'), msgs)
            print(f"Indexed: {s.get('title','')[:60]}")
    print(f"Total blobs: {len(idx.blobs)}")

# ----- Full‑text message search (uses offline conversations.json) -----
class MessageIndex:
    def __init__(self, index_dir: Path = None):
        self.index_dir = index_dir or Path.home() / 'cli-synthegration' / 'codex'
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.inverted: dict[str, set] = {}  # term -> set of (session_id, msg_idx, role, snippet)

    def load_export(self, conversations_json: Path):
        """Ingest conversations.json export (mapping tree)."""
        import re as _re
        with open(conversations_json) as f:
            data = json.load(f)
        conversations = data if isinstance(data, list) else data.get("conversations", [])
        for conv in conversations:
            sid = conv.get("id", conv.get("conversation_id", ""))
            title = conv.get("title", "")
            mapping = conv.get("mapping", {})
            for node_id, node in mapping.items():
                msg = node.get("message")
                if not msg:
                    continue
                fragments = msg.get("fragments", [])
                for frag in fragments:
                    content = frag.get("content", "")
                    if not content:
                        continue
                    ftype = frag.get("type", "")
                    role = "user" if "REQUEST" in ftype else "assistant" if "RESPONSE" in ftype else "system"
                    text = str(content).lower()
                    words = _re.findall(r"\w+", text)
                    for word in set(words):
                        self.inverted.setdefault(word, set()).add(
                            (sid, role, str(content)[:200], title)
                        )
        serializable = {k: list(v) for k, v in self.inverted.items()}
        (self.index_dir / "message_index.json").write_text(json.dumps(serializable, indent=2))
        return len(self.inverted)



    def search(self, term: str) -> list:
        """Return list of matching (session_id, title, role, snippet)."""
        term = term.lower().strip()
        if not term:
            return []
        # exact word match first, then substring
        results = set()
        for word, entries in self.inverted.items():
            if term in word:
                results.update(entries)
        # also substring search in all snippets (fallback)
        if not results:
            for entries in self.inverted.values():
                for sid, role, snippet, title in entries:
                    if term in snippet.lower() or term in title.lower():
                        results.add((sid, role, snippet, title))
        # sort by session and message index
        return sorted(results, key=lambda x: x[0])[:50]

    def search_tables(self, term: str) -> list:
        """Return tables containing the search term."""
        results = []
        for word, entries in self.inverted.items():
            if term.lower() not in word:
                continue
            for sid, role, snippet, title in entries:
                # Check if snippet contains a markdown table (has | and ---)
                if '|' in snippet and '---' in snippet:
                    results.append((sid, title, role, snippet[:300]))
        return sorted(set(results))[:20]


    @classmethod
    def load(cls, index_dir: Path = None):
        instance = cls(index_dir)
        idx_file = instance.index_dir / 'message_index.json'
        if idx_file.exists():
            data = json.loads(idx_file.read_text())
            instance.inverted = {k: set(tuple(x) for x in v) for k, v in data.items()}
        return instance

    # ----- Reverse lookup: content → origin pointer -----
    def reverse_lookup(self, text: str, min_similarity: float = 0.80) -> list:
        """Given any text, find its origin using hash→pointer index.
        Returns list of (pointer, similarity, snippet)."""
        import hashlib
        from difflib import SequenceMatcher

        # First: try exact hash match
        text_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        if text_hash in self.hash_to_pointer:
            p = self.hash_to_pointer[text_hash]
            blob = self.base_dir / 'blobs' / f'{text_hash}.blob'
            snippet = blob.read_text()[:200] if blob.exists() else ''
            return [(p, 1.0, snippet)]

        # Fallback: similarity scan (limited to avoid hangs)
        results = []
        text_sample = text[:2000]
        for ch, ptr in list(self.hash_to_pointer.items())[:200]:  # limit scan
            blob = self.base_dir / 'blobs' / f'{ch}.blob'
            if not blob.exists():
                continue
            existing = blob.read_text()
            ratio = SequenceMatcher(None, text_sample, existing[:2000]).ratio()
            if ratio >= min_similarity:
                results.append((ptr, ratio, existing[:200]))
        results.sort(key=lambda x: -x[1])
        return results[:10]
