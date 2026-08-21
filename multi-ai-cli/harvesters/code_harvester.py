#!/usr/bin/env python3
"""Code Harvester for extracting and collecting code from session chat responses.

This follows the same pattern as the Codex system in cli-synthegration:
- Extracts code blocks using lightweight regex (not BeautifulSoup)
- Creates pointers with (session_id, message_index, block_index, content_hash)
- Stores blobs in ~/.mistralai-cli/codex/blobs/{hash}.blob
- Indexes by taxonomy (language -> project -> session -> timestamp)

This allows autonomous agentic CLI interactions to directly reference
code blocks by their content hash.
"""
import os
import json
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass, field
from rich.console import Console

console = Console()


@dataclass
class Pointer:
    """Lightweight reference: (session_id, msg_idx, blk_idx) -> content_hash.
    
    This matches the Codex pattern from cli-synthegration.
    """
    session_id: str
    message_index: int
    block_index: int
    content_hash: str
    start_line: int = 0
    end_line: int = 0
    
    def to_key(self) -> str:
        """Return string key for storage."""
        return f"{self.session_id}:{self.message_index}:{self.block_index}"
    
    def citation(self) -> str:
        """Return citation format: [cursor_id Lstart-Lend]."""
        cursor_id = f"{self.session_id[:8]}:{self.message_index}:{self.block_index}"
        if self.end_line > self.start_line:
            return f"[{cursor_id} L{self.start_line}-L{self.end_line}]"
        return f"[{cursor_id} L{self.start_line}]"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON storage."""
        return {
            "session_id": self.session_id,
            "message_index": self.message_index,
            "block_index": self.block_index,
            "content_hash": self.content_hash,
            "start_line": self.start_line,
            "end_line": self.end_line,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Pointer':
        """Create from dictionary."""
        return cls(
            session_id=data.get("session_id", ""),
            message_index=data.get("message_index", 0),
            block_index=data.get("block_index", 0),
            content_hash=data.get("content_hash", ""),
            start_line=data.get("start_line", 0),
            end_line=data.get("end_line", 0),
        )


@dataclass
class CodeBlock:
    """Represents an extracted code block."""
    content: str
    language: str
    session_id: str
    message_index: int
    block_index: int
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict = field(default_factory=dict)
    content_hash: str = ""

    def __post_init__(self):
        """Compute content_hash if not provided."""
        if not self.content_hash and self.content:
            self.content_hash = hashlib.sha256(self.content.encode()).hexdigest()[:16]
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "language": self.language,
            "session_id": self.session_id,
            "message_index": self.message_index,
            "block_index": self.block_index,
            "content_hash": self.content_hash,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CodeBlock':
        """Create from dictionary."""
        return cls(
            content=data.get("content", ""),
            language=data.get("language", "text"),
            session_id=data.get("session_id", ""),
            message_index=data.get("message_index", 0),
            block_index=data.get("block_index", 0),
            content_hash=data.get("content_hash", ""),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now(timezone.utc).isoformat())),
            metadata=data.get("metadata", {}),
        )


class TaxonomyNode:
    """Hierarchical taxonomy: language -> project -> session -> timestamp.
    
    This matches the Codex pattern from cli-synthegration.
    """
    __slots__ = ('name', 'children', 'pointers', 'meta')
    
    def __init__(self, name: str):
        self.name = name
        self.children: Dict[str, 'TaxonomyNode'] = {}
        self.pointers: List[Pointer] = []
        self.meta: Dict = {}
    
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
            'pointers': [p.to_dict() for p in self.pointers],
            'children': {k: v.to_dict() for k, v in self.children.items()}
        }


class CodexIndex:
    """Content-addressed hierarchical index with pointer references.
    
    This is the MistralAI-specific implementation following the same pattern
    as cli-synthegration's CodexIndex.
    
    Key features:
    - Lightweight regex-based code extraction (no BeautifulSoup)
    - Content-addressable storage (SHA256 hash of code)
    - Hierarchical taxonomy for organization
    - Pointer-based references for autonomous agent interactions
    """
    
    # Regex pattern for extracting code blocks (same as cli-synthegration)
    CODE_BLOCK_PATTERN = re.compile(r'```(\w+)?\n(.*?)```', re.DOTALL)
    
    def __init__(self, base_dir: Path = None):
        """Initialize the Codex index."""
        self.base_dir = base_dir or Path.home() / '.mistralai-cli' / 'codex'
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Taxonomy root
        self.taxonomy = TaxonomyNode("root")
        
        # Content storage
        self.blobs: Dict[str, str] = {}  # content_hash -> blob_path
        self.time_index: Dict[str, datetime] = {}  # content_hash -> timestamp
        self.hash_to_pointer: Dict[str, Pointer] = {}  # content_hash -> Pointer
        
        # Load existing index
        self._load()
        self._rebuild_hash_index()
    
    def _load(self):
        """Load index from disk."""
        index_file = self.base_dir / 'codex_index.json'
        if index_file.exists():
            try:
                data = json.loads(index_file.read_text())
                self._from_flat(data)
            except Exception as e:
                console.print(f"[yellow]Warning: Failed to load codex index: {e}[/yellow]")
    
    def _from_flat(self, data: dict):
        """Rebuild index from flat JSON format."""
        for ptr_data in data.get('pointers', []):
            p = Pointer(
                session_id=ptr_data.get('sid', ptr_data.get('session_id', '')),
                message_index=ptr_data.get('mi', ptr_data.get('message_index', 0)),
                block_index=ptr_data.get('bi', ptr_data.get('block_index', 0)),
                content_hash=ptr_data.get('ch', ptr_data.get('content_hash', '')),
            )
            path = ptr_data.get('path', ['uncategorized'])
            self.taxonomy.add_pointer(p, path)
            ts = ptr_data.get('ts')
            if ts:
                try:
                    self.time_index[p.content_hash] = datetime.fromisoformat(ts)
                except Exception:
                    pass
    
    def _rebuild_hash_index(self):
        """Rebuild blobs dict and hash->pointer by scanning disk."""
        blob_dir = self.base_dir / "blobs"
        if not blob_dir.exists():
            return
        for blob_file in blob_dir.glob("*.blob"):
            ch = blob_file.stem
            self.blobs[ch] = str(blob_file)
            if ch not in self.hash_to_pointer:
                self.hash_to_pointer[ch] = Pointer("imported", 0, 0, ch)
    
    def _save(self):
        """Save index to disk."""
        flat = {'pointers': [], 'version': 1}
        
        def flatten(node, path):
            for p in node.pointers:
                flat['pointers'].append({
                    'sid': p.session_id,
                    'mi': p.message_index,
                    'bi': p.block_index,
                    'ch': p.content_hash,
                    'path': path,
                    'ts': self.time_index.get(p.content_hash, datetime.now(timezone.utc)).isoformat()
                })
            for name, child in node.children.items():
                flatten(child, path + [name])
        
        flatten(self.taxonomy, ['root'])
        (self.base_dir / 'codex_index.json').write_text(json.dumps(flat, indent=2))
    
    def index_conversation(self, session_id: str, title: str, messages: List[dict]):
        """Index all code blocks from a conversation into the taxonomy.
        
        This is the main entry point called after fetching session messages.
        It extracts code blocks using regex and stores them in the codex.
        
        Args:
            session_id: The session identifier
            title: Session title (used for taxonomy path)
            messages: List of message dictionaries with 'content' and 'role' keys
        """
        project = self._safe_name(title)
        
        for msg_idx, msg in enumerate(messages):
            content = msg.get('content', '')
            role = msg.get('role', 'unknown')
            ts = msg.get('inserted_at', msg.get('timestamp', ''))
            
            # Extract code blocks using regex (same pattern as cli-synthegration)
            for blk_idx, match in enumerate(self.CODE_BLOCK_PATTERN.finditer(content)):
                lang = (match.group(1) or 'text').lower()
                code = match.group(2)
                
                # Create content hash (SHA256, first 16 chars like cli-synthegration)
                ch = hashlib.sha256(code.encode()).hexdigest()[:16]
                
                # Create pointer
                p = Pointer(session_id, msg_idx, blk_idx, ch)
                
                # Add to taxonomy: language -> project -> role
                path = [lang, project, role]
                self.taxonomy.add_pointer(p, path)
                
                # Store timestamp
                if ts:
                    try:
                        self.time_index[ch] = datetime.fromisoformat(ts)
                    except Exception:
                        self.time_index[ch] = datetime.now(timezone.utc)
                else:
                    self.time_index[ch] = datetime.now(timezone.utc)
                
                # Store blob if not already present
                blob_path = self.base_dir / 'blobs' / f"{ch}.blob"
                blob_path.parent.mkdir(exist_ok=True)
                if not blob_path.exists():
                    blob_path.write_text(code)
                
                self.blobs[ch] = str(blob_path)
                self.hash_to_pointer[ch] = p
        
        # Save index
        self._save()
        
        console.print(f"[green]Indexed {len(self.blobs)} code blocks from session {session_id[:8]}[/green]")
    
    def index_session_file(self, session_file: Path):
        """Index a session JSON file.
        
        Args:
            session_file: Path to a session JSON file (from session_store)
        """
        if not session_file.exists():
            console.print(f"[red]Session file not found: {session_file}[/red]")
            return
        
        try:
            with open(session_file) as f:
                messages = json.load(f)
        except Exception as e:
            console.print(f"[red]Failed to load session file: {e}[/red]")
            return
        
        # Extract session_id from filename or first message
        session_id = session_file.stem
        title = session_file.stem.replace('_', ' ')
        
        self.index_conversation(session_id, title, messages)
    
    def extract_from_messages(self, messages: List[dict], session_id: str = "temp", title: str = "temp") -> List[CodeBlock]:
        """Extract code blocks from a list of messages.
        
        Args:
            messages: List of message dictionaries
            session_id: Session identifier
            title: Session title
            
        Returns:
            List of extracted CodeBlock objects
        """
        code_blocks = []
        
        for msg_idx, msg in enumerate(messages):
            content = msg.get('content', '')
            role = msg.get('role', 'unknown')
            
            for blk_idx, match in enumerate(self.CODE_BLOCK_PATTERN.finditer(content)):
                lang = (match.group(1) or 'text').lower()
                code = match.group(2)
                ch = hashlib.sha256(code.encode()).hexdigest()[:16]
                
                code_block = CodeBlock(
                    content=code,
                    language=lang,
                    session_id=session_id,
                    message_index=msg_idx,
                    block_index=blk_idx,
                    content_hash=ch,
                    metadata={
                        "role": role,
                        "source": "session",
                    }
                )
                code_blocks.append(code_block)
        
        return code_blocks
    
    def get_code_by_hash(self, content_hash: str) -> Optional[str]:
        """Get code content by its hash.
        
        Args:
            content_hash: The SHA256 hash (first 16 chars) of the code
            
        Returns:
            The code content, or None if not found
        """
        blob_path = self.blobs.get(content_hash)
        if blob_path and Path(blob_path).exists():
            return Path(blob_path).read_text()
        return None
    
    def get_pointer_by_hash(self, content_hash: str) -> Optional[Pointer]:
        """Get pointer by content hash.
        
        Args:
            content_hash: The SHA256 hash (first 16 chars) of the code
            
        Returns:
            The Pointer object, or None if not found
        """
        return self.hash_to_pointer.get(content_hash)
    
    def search(self, term: str, language: str = None) -> List[Dict]:
        """Search code blocks by term and optional language filter.
        
        Args:
            term: Search term
            language: Optional language filter
            
        Returns:
            List of search results with code content
        """
        results = []
        
        # Search all blobs for the term
        for ch, blob_path in self.blobs.items():
            if Path(blob_path).exists():
                code = Path(blob_path).read_text()
                if term.lower() in code.lower():
                    # Get pointer
                    p = self.hash_to_pointer.get(ch)
                    if p:
                        # Filter by language if specified
                        if language:
                            # Get the language from taxonomy
                            # For now, check if the code block is in the specified language
                            # by checking the first part of the taxonomy path
                            lang_node = self.taxonomy.children.get(language.lower())
                            if lang_node:
                                # Check if this hash is in the language node
                                if not self._is_hash_in_node(lang_node, ch):
                                    continue
                        
                        results.append({
                            'pointer': p.to_key(),
                            'hash': ch,
                            'code': code[:200] + '...' if len(code) > 200 else code,
                            'timestamp': self.time_index.get(ch, '').isoformat(),
                            'session_id': p.session_id,
                            'message_index': p.message_index,
                            'block_index': p.block_index,
                        })
        
        return results
    
    def _is_hash_in_node(self, node, content_hash: str) -> bool:
        """Check if a hash exists in a taxonomy node or its children."""
        for p in node.pointers:
            if p.content_hash == content_hash:
                return True
        for child in node.children.values():
            if self._is_hash_in_node(child, content_hash):
                return True
        return False
    
    def search_by_language(self, language: str, term: str = "") -> List[Dict]:
        """Search code blocks by language.
        
        Args:
            language: Language to filter by
            term: Optional additional search term
            
        Returns:
            List of search results
        """
        # Search the taxonomy for the language
        lang_node = self.taxonomy.children.get(language.lower())
        if not lang_node:
            return []
        
        results = []
        
        # Collect all pointers under this language
        def collect_pointers(node):
            pointers = []
            pointers.extend(node.pointers)
            for child in node.children.values():
                pointers.extend(collect_pointers(child))
            return pointers
        
        pointers = collect_pointers(lang_node)
        
        for p in pointers:
            code = self.get_code_by_hash(p.content_hash)
            if code and (not term or term.lower() in code.lower()):
                results.append({
                    'pointer': p.to_key(),
                    'hash': p.content_hash,
                    'code': code[:200] + '...' if len(code) > 200 else code,
                    'timestamp': self.time_index.get(p.content_hash, '').isoformat(),
                    'session_id': p.session_id,
                    'message_index': p.message_index,
                    'block_index': p.block_index,
                })
        
        return results
    
    def get_all_blocks(self) -> List[CodeBlock]:
        """Get all code blocks in the index.
        
        Returns:
            List of all CodeBlock objects
        """
        code_blocks = []
        
        def traverse(node, path=[]):
            for p in node.pointers:
                code = self.get_code_by_hash(p.content_hash)
                if code:
                    code_block = CodeBlock(
                        content=code,
                        language=path[0] if path else "text",
                        session_id=p.session_id,
                        message_index=p.message_index,
                        block_index=p.block_index,
                        content_hash=p.content_hash,
                        timestamp=self.time_index.get(p.content_hash, datetime.now(timezone.utc)),
                        metadata={"path": path}
                    )
                    code_blocks.append(code_block)
            for child in node.children.values():
                traverse(child, path + [child.name])
        
        traverse(self.taxonomy)
        return code_blocks
    
    def get_stats(self) -> Dict:
        """Get index statistics.
        
        Returns:
            Dictionary with index statistics
        """
        def count_pointers(node):
            count = len(node.pointers)
            for child in node.children.values():
                count += count_pointers(child)
            return count
        
        return {
            "total_blocks": len(self.blobs),
            "total_pointers": count_pointers(self.taxonomy),
            "languages": list(self.taxonomy.children.keys()),
        }
    
    @staticmethod
    def _safe_name(name: str) -> str:
        """Sanitize name for use in taxonomy path."""
        return re.sub(r'[\\/*?:"<>|\[\]\s]', '_', name)[:60]


class CodeHarvester:
    """Harvests code from files, directories, session responses, and other sources.
    
    This is the main interface for code harvesting, which uses CodexIndex
    internally for session-based code extraction.
    """
    
    # Language extensions mapping
    LANGUAGE_EXTENSIONS = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.java': 'java',
        '.c': 'c',
        '.cpp': 'cpp',
        '.h': 'c',
        '.hpp': 'cpp',
        '.go': 'go',
        '.rs': 'rust',
        '.rb': 'ruby',
        '.php': 'php',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.sh': 'bash',
        '.bash': 'bash',
        '.zsh': 'bash',
        '.sql': 'sql',
        '.html': 'html',
        '.css': 'css',
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.xml': 'xml',
        '.md': 'markdown',
    }
    
    def __init__(self, codex_dir: Path = None):
        """Initialize the harvester."""
        self.codex = CodexIndex(codex_dir)
        self.snippets: List[CodeBlock] = []
    
    def harvest_from_session(self, session_id: str, messages: List[dict], title: str = None) -> List[CodeBlock]:
        """Harvest code from a session's messages.
        
        This is the primary method for harvesting code from MistralAI chat sessions.
        It extracts code blocks and indexes them in the Codex.
        
        Args:
            session_id: The session identifier
            messages: List of message dictionaries with 'content' and 'role' keys
            title: Optional session title for taxonomy
            
        Returns:
            List of extracted CodeBlock objects
        """
        if title is None:
            title = session_id[:8]
        
        # Index in codex
        self.codex.index_conversation(session_id, title, messages)
        
        # Also return as CodeBlock objects
        code_blocks = self.codex.extract_from_messages(messages, session_id, title)
        self.snippets.extend(code_blocks)
        
        return code_blocks
    
    def harvest_from_session_file(self, session_file: Path) -> List[CodeBlock]:
        """Harvest code from a session JSON file.
        
        Args:
            session_file: Path to a session JSON file
            
        Returns:
            List of extracted CodeBlock objects
        """
        self.codex.index_session_file(session_file)
        
        # Load and extract
        try:
            with open(session_file) as f:
                messages = json.load(f)
            session_id = session_file.stem
            title = session_file.stem.replace('_', ' ')
            code_blocks = self.codex.extract_from_messages(messages, session_id, title)
            self.snippets.extend(code_blocks)
            return code_blocks
        except Exception as e:
            console.print(f"[red]Failed to harvest from session file: {e}[/red]")
            return []
    
    def harvest_from_text(self, text: str, source: str = "text") -> List[CodeBlock]:
        """Extract code blocks from plain text.
        
        Args:
            text: The text to extract code from
            source: Source identifier
            
        Returns:
            List of extracted CodeBlock objects
        """
        code_blocks = []
        
        for blk_idx, match in enumerate(CodexIndex.CODE_BLOCK_PATTERN.finditer(text)):
            lang = (match.group(1) or 'text').lower()
            code = match.group(2)
            ch = hashlib.sha256(code.encode()).hexdigest()[:16]
            
            code_block = CodeBlock(
                content=code,
                language=lang,
                session_id=source,
                message_index=0,
                block_index=blk_idx,
                content_hash=ch,
                metadata={"source": source}
            )
            code_blocks.append(code_block)
        
        self.snippets.extend(code_blocks)
        return code_blocks
    
    def harvest_file(self, file_path: str, language: str = None) -> List[CodeBlock]:
        """Harvest code from a single file.
        
        Args:
            file_path: Path to the file
            language: Optional language override
            
        Returns:
            List of CodeBlock objects (one per file for non-markdown)
        """
        path = Path(file_path)
        if not path.exists():
            console.print(f"[red]File not found: {file_path}[/red]")
            return []
        
        try:
            content = path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            try:
                content = path.read_text(encoding='latin-1')
            except Exception as e:
                console.print(f"[red]Failed to read {file_path}: {e}[/red]")
                return []
        
        # Determine language
        lang = language or self._detect_language(file_path)
        
        # For markdown files, extract code blocks
        if lang == "markdown":
            return self.harvest_from_text(content, file_path)
        
        # For other files, treat entire file as code
        ch = hashlib.sha256(content.encode()).hexdigest()[:16]
        
        code_block = CodeBlock(
            content=content,
            language=lang,
            session_id=file_path,
            message_index=0,
            block_index=0,
            content_hash=ch,
            metadata={"file_type": "source", "file_path": file_path}
        )
        
        self.snippets.append(code_block)
        return [code_block]
    
    def harvest_directory(self, dir_path: str, recursive: bool = True, patterns: List[str] = None) -> List[CodeBlock]:
        """Harvest code from a directory.
        
        Args:
            dir_path: Path to the directory
            recursive: Whether to recurse into subdirectories
            patterns: Optional list of file patterns to include
            
        Returns:
            List of extracted CodeBlock objects
        """
        path = Path(dir_path)
        if not path.exists():
            console.print(f"[red]Directory not found: {dir_path}[/red]")
            return []
        
        harvested = []
        
        for root, dirs, files in os.walk(dir_path):
            if not recursive:
                dirs.clear()
            
            for file in files:
                file_path = Path(root) / file
                
                # Filter by patterns if provided
                if patterns:
                    if not any(file.endswith(p) or file.endswith(p.upper()) for p in patterns):
                        continue
                
                # Skip hidden files and common non-code directories
                if file.startswith('.'):
                    continue
                if file in ['__pycache__', '.git', '.svn', 'node_modules', 'venv', '.venv']:
                    continue
                
                # Harvest the file
                snippets = self.harvest_file(str(file_path))
                harvested.extend(snippets)
        
        return harvested
    
    def _detect_language(self, file_path: str) -> str:
        """Detect language from file extension."""
        ext = Path(file_path).suffix.lower()
        return self.LANGUAGE_EXTENSIONS.get(ext, "text")
    
    def get_codex(self) -> CodexIndex:
        """Get the underlying CodexIndex."""
        return self.codex
    
    def search(self, query: str, language: str = None) -> List[Dict]:
        """Search harvested code.
        
        Args:
            query: Search query
            language: Optional language filter
            
        Returns:
            List of search results
        """
        return self.codex.search(query, language)
    
    def get_by_hash(self, content_hash: str) -> Optional[str]:
        """Get code content by hash.
        
        Args:
            content_hash: The content hash
            
        Returns:
            The code content, or None if not found
        """
        return self.codex.get_code_by_hash(content_hash)
    
    def get_stats(self) -> Dict:
        """Get harvesting statistics.
        
        Returns:
            Dictionary with statistics
        """
        codex_stats = self.codex.get_stats()
        return {
            **codex_stats,
            "harvested_snippets": len(self.snippets),
        }
    
    def clear(self):
        """Clear all harvested snippets (but keep codex)."""
        self.snippets.clear()


if __name__ == "__main__":
    # Example usage
    harvester = CodeHarvester()
    
    # Test with sample messages (like from MistralAI session)
    sample_messages = [
        {
            "role": "user",
            "content": "Can you write a Python function to sort a list?",
            "message_id": 1,
        },
        {
            "role": "assistant",
            "content": "Here's a Python function:\n\n```python\ndef sort_list(lst):\n    return sorted(lst)\n```\n\nYou can use it like this: `sorted = sort_list([3, 1, 2])`",
            "message_id": 2,
        },
    ]
    
    # Harvest from session
    code_blocks = harvester.harvest_from_session("test_session_123", sample_messages, "Test Session")
    
    print(f"Harvested {len(code_blocks)} code blocks")
    for block in code_blocks:
        print(f"  - {block.language}: {block.content_hash}")
        print(f"    Content: {block.content[:50]}...")
    
    # Search
    results = harvester.search("sort")
    print(f"\nFound {len(results)} results for 'sort'")
    for result in results:
        print(f"  - {result['hash']}: {result['code'][:50]}...")
