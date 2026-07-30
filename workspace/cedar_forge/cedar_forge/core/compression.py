"""Unified compression layer using CedrLang + CedarIndex."""
import sys
import re
from pathlib import Path

# Add parent to path to import cedrlang and cid
sys.path.insert(0, str(Path.home() / "workspace/compression_sandbox/cedrlang"))

try:
    from cedrlang import compress as cedr_compress, expand as cedr_expand
    from cid import CedarIndex
    HAS_CEDAR = True
except ImportError as e:
    HAS_CEDAR = False
    print(f"Warning: compression libs not found: {e}", file=sys.stderr)

class Compressor:
    def __init__(self):
        self.ci = CedarIndex() if HAS_CEDAR else None

    def compress_prompt(self, text: str, aggressive: bool = True) -> str:
        """Compress natural language prompt + replace CEDARscript commands with pointers."""
        if not HAS_CEDAR:
            return text
        # Step 1: Compress natural language (stopwords + symbols)
        compressed = cedr_compress(text, aggressive=aggressive)
        # Step 2: Replace any CEDARscript command with its pointer
        # (heuristic: commands start with CREATE, UPDATE, INSERT, DELETE, MOVE, SELECT, RENAME, etc.)
        for cmd in self._extract_commands(compressed):
            ptr = self.ci.compress(cmd)
            compressed = compressed.replace(cmd, ptr)
        return compressed

    def expand_response(self, text: str) -> str:
        """Expand pointers in LLM response back to human‑readable."""
        if not HAS_CEDAR:
            return text
        # Replace known pointers
        pattern = re.escape(CedarIndex.PREFIX) + r'[a-z0-9]{4}'
        def repl(m):
            ptr = m.group(0)
            expanded = self.ci.expand(ptr)
            return expanded if expanded else ptr
        return re.sub(pattern, repl, text)

    def _extract_commands(self, text: str):
        """Very naive extraction – improve with actual parsing later."""
        keywords = ['CREATE', 'UPDATE', 'INSERT', 'DELETE', 'MOVE', 'SELECT', 'RENAME', 'EXTRACT', 'INLINE', 'ADD', 'REMOVE']
        # Split on punctuation/space and find multi‑word commands
        words = text.split()
        cmds = []
        for i, w in enumerate(words):
            if w.upper() in keywords:
                # capture up to next newline or period
                end = i+1
                while end < len(words) and not words[end].endswith(('.', ';', '!')):
                    end += 1
                cmd = ' '.join(words[i:end])
                cmds.append(cmd)
        return cmds

# Singleton
_compressor = None
def get_compressor():
    global _compressor
    if _compressor is None:
        _compressor = Compressor()
    return _compressor
