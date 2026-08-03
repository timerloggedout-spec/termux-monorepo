import json
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass, field
from archwiz.config import ARCHWIZ_ROOT

@dataclass
class Pointer:
    """Lightweight reference: (session_id, msg_idx, blk_idx) -> content_hash."""
    session_id: str
    message_index: int
    block_index: int
    content_hash: str
    start_line: int = 0
    end_line: int = 0
    
    def to_key(self) -> str:
        return f"{self.session_id}:{self.message_index}:{self.block_index}"
    
    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "message_index": self.message_index,
            "block_index": self.block_index,
            "content_hash": self.content_hash,
            "start_line": self.start_line,
            "end_line": self.end_line,
        }

@dataclass
class CodeBlock:
    """Represents an extracted code block."""
    content: str
    language: str
    session_id: str
    message_index: int
    block_index: int
    provider: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict = field(default_factory=dict)
    content_hash: str = ""

    def __post_init__(self):
        if not self.content_hash and self.content:
            self.content_hash = hashlib.sha256(self.content.encode()).hexdigest()[:16]

class CodexIndex:
    """
    Content-addressed hierarchical index for code blocks.
    Salvaged and normalized from PR #6 (TER-9).
    """
    CODE_BLOCK_PATTERN = re.compile(r'```(\w+)?\n(.*?)```', re.DOTALL)
    
    def __init__(self, provider: str = "global"):
        self.provider = provider
        self.base_dir = ARCHWIZ_ROOT / ".archwiz" / "codex" / provider
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.blobs_dir = self.base_dir / "blobs"
        self.blobs_dir.mkdir(exist_ok=True)
        
        self.index_file = self.base_dir / "index.json"
        self.pointers: List[Pointer] = []
        self.blobs: Dict[str, str] = {}  # hash -> path
        
        self._load()

    def _load(self):
        if self.index_file.exists():
            try:
                data = json.loads(self.index_file.read_text())
                for p_data in data.get("pointers", []):
                    self.pointers.append(Pointer(**p_data))
            except Exception:
                pass
        
        for blob_file in self.blobs_dir.glob("*.blob"):
            self.blobs[blob_file.stem] = str(blob_file)

    def _save(self):
        data = {
            "version": 1,
            "provider": self.provider,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "pointers": [p.to_dict() for p in self.pointers]
        }
        self.index_file.write_text(json.dumps(data, indent=2))

    def harvest(self, session_id: str, messages: List[Dict[str, Any]]) -> int:
        """Extract and index code blocks from messages."""
        count = 0
        for msg_idx, msg in enumerate(messages):
            content = msg.get("content", "")
            for blk_idx, match in enumerate(self.CODE_BLOCK_PATTERN.finditer(content)):
                lang = (match.group(1) or "text").lower()
                code = match.group(2)
                ch = hashlib.sha256(code.encode()).hexdigest()[:16]
                
                # Store blob
                blob_path = self.blobs_dir / f"{ch}.blob"
                if not blob_path.exists():
                    blob_path.write_text(code)
                self.blobs[ch] = str(blob_path)
                
                # Record pointer
                p = Pointer(session_id, msg_idx, blk_idx, ch)
                self.pointers.append(p)
                count += 1
        
        if count > 0:
            self._save()
        return count

    def get_code(self, content_hash: str) -> Optional[str]:
        path = self.blobs.get(content_hash)
        if path and Path(path).exists():
            return Path(path).read_text()
        return None
