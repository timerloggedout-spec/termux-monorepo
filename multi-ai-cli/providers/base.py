#!/usr/bin/env python3
"""Base provider interface with Codex harvesting support."""
import os
import json
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
from abc import ABC, abstractmethod
from rich.console import Console

console = Console()


@dataclass
class ProviderConfig:
    """Configuration for a provider."""
    name: str
    api_url: str = ""
    token_path: str = ""
    cookie_path: str = ""
    model: str = ""
    timeout: int = 30
    max_tokens: int = 4096
    temperature: float = 0.7
    extra_headers: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ProviderConfig':
        """
        Create a provider configuration from a dictionary of settings.
        
        Parameters:
        	data (Dict): Configuration values keyed by provider setting name.
        
        Returns:
        	ProviderConfig: A configuration populated with recognized settings.
        """
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class ProviderType:
    """Provider types enumeration."""
    MISTRAL = "mistral"
    DEEPSEEK = "deepseek"
    CLAUDE = "claude"
    GEMINI = "gemini"
    COLAB = "colab"
    AI_STUDIO = "ai_studio"
    ANTHROPIC = "anthropic"
    DUCKDUCKGO = "duckduckgo"
    GROK = "grok"
    KIMI = "kimi"
    OPENAI = "openai"
    PERPLEXITY = "perplexity"
    QWEN = "qwen"


@dataclass
class Pointer:
    """Lightweight reference: (session_id, msg_idx, blk_idx) -> content_hash.
    
    Used by all providers for content-addressable code blocks.
    """
    session_id: str
    message_index: int
    block_index: int
    content_hash: str
    start_line: int = 0
    end_line: int = 0
    
    def to_key(self) -> str:
        """
        Create a storage key from the session, message, and block identifiers.
        
        Returns:
        	str: A colon-delimited key containing the session ID, message index, and block index.
        """
        return f"{self.session_id}:{self.message_index}:{self.block_index}"
    
    def citation(self) -> str:
        """
        Format the code block reference as a compact citation.
        
        Returns:
        	str: A citation containing the session identifier, message and block indices, and line range.
        """
        cursor_id = f"{self.session_id[:8]}:{self.message_index}:{self.block_index}"
        if self.end_line > self.start_line:
            return f"[{cursor_id} L{self.start_line}-L{self.end_line}]"
        return f"[{cursor_id} L{self.start_line}]"
    
    def to_dict(self) -> Dict:
        """
        Serialize the pointer identifiers and optional line range to a dictionary.
        
        Returns:
        	dict: A dictionary containing the session, message, block, content-hash, and line-range metadata.
        """
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
    """Represents an extracted code block from any provider."""
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
        """
        Compute a content hash when the code block has content but no existing hash.
        """
        if not self.content_hash and self.content:
            self.content_hash = hashlib.sha256(self.content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict:
        """
        Serialize the code block's content and metadata as a dictionary.
        
        Returns:
        	dict: A dictionary containing the code block fields, with the timestamp represented as an ISO 8601 string.
        """
        return {
            "content": self.content,
            "language": self.language,
            "session_id": self.session_id,
            "message_index": self.message_index,
            "block_index": self.block_index,
            "provider": self.provider,
            "content_hash": self.content_hash,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


class TaxonomyNode:
    """Hierarchical taxonomy: language -> project -> session -> timestamp."""
    __slots__ = ('name', 'children', 'pointers', 'meta')
    
    def __init__(self, name: str):
        """Initialize a taxonomy node with the given name and empty children, pointers, and metadata."""
        self.name = name
        self.children: Dict[str, 'TaxonomyNode'] = {}
        self.pointers: List[Pointer] = []
        self.meta: Dict = {}
    
    def add_pointer(self, pointer: Pointer, path: List[str]):
        """Insert pointer along a hierarchical path."""
        node = self
        for part in path:
            if part not in node.children:
                node.children[part] = TaxonomyNode(part)
            node = node.children[part]
        node.pointers.append(pointer)
    
    def search(self, term: str) -> List[Pointer]:
        """
        Find pointers in this node and its descendants whose names contain a search term.
        
        Parameters:
            term (str): Case-insensitive text to search for in node names.
        
        Returns:
            List[Pointer]: Pointers stored in matching nodes.
        """
        results = []
        if term.lower() in self.name.lower():
            results.extend(self.pointers)
        for child in self.children.values():
            results.extend(child.search(term))
        return results


class CodexIndex:
    """Content-addressed hierarchical index for code blocks.
    
    Shared by all providers for consistent code block storage and retrieval.
    """
    
    # Regex pattern for extracting code blocks (same as cli-synthegration)
    CODE_BLOCK_PATTERN = re.compile(r'```(\w+)?\n(.*?)```', re.DOTALL)
    
    def __init__(self, base_dir: Path = None, provider: str = None):
        """
        Initialize a persistent code index for an optional provider.
        
        Parameters:
            base_dir (Path, optional): Directory used to store index data and code blobs. Defaults to the provider-specific Codex directory in the user's home directory.
            provider (str, optional): Provider associated with the index. Defaults to the global index.
        """
        self.provider = provider
        self.base_dir = base_dir or Path.home() / '.multi-ai-cli' / 'codex' / (provider or 'global')
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.taxonomy = TaxonomyNode("root")
        self.blobs: Dict[str, str] = {}
        self.time_index: Dict[str, datetime] = {}
        self.hash_to_pointer: Dict[str, Pointer] = {}
        self.provider_index: Dict[str, List[str]] = {}  # provider -> list of hashes
        
        self._load()
        self._rebuild_hash_index()
    
    def _load(self):
        """
        Load the persisted code index from disk when the index file exists.
        
        Malformed or unreadable index data is skipped and a warning is displayed.
        """
        index_file = self.base_dir / 'codex_index.json'
        if index_file.exists():
            try:
                data = json.loads(index_file.read_text())
                self._from_flat(data)
            except Exception as e:
                console.print(f"[yellow]Warning: Failed to load codex index: {e}[/yellow]")
    
    def _from_flat(self, data: dict):
        """
        Reconstruct index entries from serialized flat data.
        
        Parameters:
        	data (dict): Flat index data containing pointer records, taxonomy paths, timestamps, and provider associations.
        """
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
            
            # Track provider
            provider = ptr_data.get('provider', 'unknown')
            if provider not in self.provider_index:
                self.provider_index[provider] = []
            self.provider_index[provider].append(p.content_hash)
    
    def _rebuild_hash_index(self):
        """Rebuild hash index from disk."""
        blob_dir = self.base_dir / "blobs"
        if not blob_dir.exists():
            return
        for blob_file in blob_dir.glob("*.blob"):
            ch = blob_file.stem
            self.blobs[ch] = str(blob_file)
            if ch not in self.hash_to_pointer:
                self.hash_to_pointer[ch] = Pointer("imported", 0, 0, ch)
    
    def _save(self):
        """
        Persist the current code index, including pointers, taxonomy paths, timestamps, and provider metadata, to disk.
        """
        flat = {'pointers': [], 'version': 1}
        
        def flatten(node, path):
            """
            Append node pointers and their metadata to the flattened index representation.
            
            Parameters:
                node (TaxonomyNode): Taxonomy node whose pointers and descendants are serialized.
                path (list[str]): Path of node names leading to the current node.
            """
            for p in node.pointers:
                flat['pointers'].append({
                    'sid': p.session_id,
                    'mi': p.message_index,
                    'bi': p.block_index,
                    'ch': p.content_hash,
                    'path': path,
                    'ts': self.time_index.get(p.content_hash, datetime.now(timezone.utc)).isoformat(),
                    'provider': self.provider or 'unknown',
                })
            for name, child in node.children.items():
                flatten(child, path + [name])
        
        flatten(self.taxonomy, ['root'])
        (self.base_dir / 'codex_index.json').write_text(json.dumps(flat, indent=2))
    
    def index_conversation(self, session_id: str, title: str, messages: List[dict], provider: str = None):
        """
        Index fenced code blocks from a conversation and persist their content and metadata.
        
        Parameters:
        	session_id (str): Identifier of the conversation session.
        	title (str): Conversation title used to organize indexed blocks.
        	messages (List[dict]): Conversation messages containing content and optional role and timestamp fields.
        	provider (str, optional): Provider associated with the conversation.
        """
        project = self._safe_name(title)
        
        for msg_idx, msg in enumerate(messages):
            content = msg.get('content', '')
            role = msg.get('role', 'unknown')
            ts = msg.get('inserted_at', msg.get('timestamp', ''))
            
            for blk_idx, match in enumerate(self.CODE_BLOCK_PATTERN.finditer(content)):
                lang = (match.group(1) or 'text').lower()
                code = match.group(2)
                ch = hashlib.sha256(code.encode()).hexdigest()[:16]
                
                p = Pointer(session_id, msg_idx, blk_idx, ch)
                path = [lang, project, role]
                self.taxonomy.add_pointer(p, path)
                
                if ts:
                    try:
                        self.time_index[ch] = datetime.fromisoformat(ts)
                    except Exception:
                        self.time_index[ch] = datetime.now(timezone.utc)
                else:
                    self.time_index[ch] = datetime.now(timezone.utc)
                
                blob_path = self.base_dir / 'blobs' / f"{ch}.blob"
                blob_path.parent.mkdir(exist_ok=True)
                if not blob_path.exists():
                    blob_path.write_text(code)
                
                self.blobs[ch] = str(blob_path)
                self.hash_to_pointer[ch] = p
                
                # Track provider
                prov = provider or self.provider or 'unknown'
                if prov not in self.provider_index:
                    self.provider_index[prov] = []
                if ch not in self.provider_index[prov]:
                    self.provider_index[prov].append(ch)
        
        self._save()
        console.print(f"[green][{provider or 'global'}] Indexed {len(self.blobs)} code blocks from session {session_id[:8]}[/green]")
    
    def extract_from_messages(self, messages: List[dict], session_id: str = "temp", title: str = "temp", provider: str = None) -> List[CodeBlock]:
        """
        Extract fenced code blocks from conversation messages.
        
        Parameters:
        	messages (List[dict]): Messages containing content and role fields.
        	session_id (str): Identifier for the conversation.
        	title (str): Conversation title retained for compatibility.
        	provider (str): Provider associated with the extracted code blocks.
        
        Returns:
        	List[CodeBlock]: Extracted code blocks with language, message position, provider, and source metadata.
        """
        code_blocks = []
        
        for msg_idx, msg in enumerate(messages):
            content = msg.get('content', '')
            role = msg.get('role', 'unknown')
            
            for blk_idx, match in enumerate(self.CODE_BLOCK_PATTERN.finditer(content)):
                lang = (match.group(1) or 'text').lower()
                code = match.group(2).strip()
                ch = hashlib.sha256(code.encode()).hexdigest()[:16]
                
                code_block = CodeBlock(
                    content=code,
                    language=lang,
                    session_id=session_id,
                    message_index=msg_idx,
                    block_index=blk_idx,
                    provider=provider or self.provider or 'unknown',
                    metadata={"role": role, "source": "session"}
                )
                code_blocks.append(code_block)
        
        return code_blocks
    
    def search(self, term: str, language: str = None, provider: str = None) -> List[Dict]:
        """
        Search indexed code blocks for a term, optionally filtered by language and provider.
        
        Parameters:
            term (str): Case-insensitive text to find in the stored code.
            language (str, optional): Language used to filter matching code blocks.
            provider (str, optional): Provider used to filter matching code blocks.
        
        Returns:
            List[Dict]: Matching code-block metadata, including its pointer, hash, truncated code, timestamp, location, and provider.
        """
        results = []
        
        # Filter by provider if specified
        hashes_to_search = None
        if provider:
            hashes_to_search = set(self.provider_index.get(provider, []))
        
        for ch, blob_path in self.blobs.items():
            # Filter by provider
            if hashes_to_search and ch not in hashes_to_search:
                continue
            
            if Path(blob_path).exists():
                code = Path(blob_path).read_text()
                if term.lower() in code.lower():
                    p = self.hash_to_pointer.get(ch)
                    if p:
                        # Filter by language if specified
                        if language:
                            lang_node = self.taxonomy.children.get(language.lower())
                            if lang_node and not self._is_hash_in_node(lang_node, ch):
                                continue
                        
                        results.append({
                            'pointer': p.to_key(),
                            'hash': ch,
                            'code': code[:200] + '...' if len(code) > 200 else code,
                            'timestamp': self.time_index.get(ch, '').isoformat(),
                            'session_id': p.session_id,
                            'message_index': p.message_index,
                            'block_index': p.block_index,
                            'provider': self.provider or 'unknown',
                        })
        
        return results
    
    def _is_hash_in_node(self, node, content_hash: str) -> bool:
        """Check if hash exists in node or children."""
        for p in node.pointers:
            if p.content_hash == content_hash:
                return True
        for child in node.children.values():
            if self._is_hash_in_node(child, content_hash):
                return True
        return False
    
    def get_code_by_hash(self, content_hash: str) -> Optional[str]:
        """
        Retrieve stored code using its content hash.
        
        Parameters:
        	content_hash (str): The hash identifying the stored code.
        
        Returns:
        	str: The stored code, or None if no matching blob is available.
        """
        blob_path = self.blobs.get(content_hash)
        if blob_path and Path(blob_path).exists():
            return Path(blob_path).read_text()
        return None
    
    def get_by_provider(self, provider: str) -> List[Dict]:
        """
        Retrieve indexed code blocks associated with a provider.
        
        Parameters:
        	provider (str): Provider name used to filter the indexed code blocks.
        
        Returns:
        	List[Dict]: Code block records containing the hash, code preview, provider name, and session ID.
        """
        results = []
        for ch in self.provider_index.get(provider, []):
            code = self.get_code_by_hash(ch)
            p = self.hash_to_pointer.get(ch)
            if code and p:
                results.append({
                    'hash': ch,
                    'code': code[:200] + '...' if len(code) > 200 else code,
                    'provider': provider,
                    'session_id': p.session_id,
                })
        return results
    
    @staticmethod
    def _safe_name(name: str) -> str:
        """Sanitize a taxonomy name for safe storage.
        
        Parameters:
        	name (str): The taxonomy name to sanitize.
        
        Returns:
        	str: The name with unsafe characters replaced by underscores and limited to 60 characters.
        """
        return re.sub(r'[\\/*?:"<>|\[\]\s]', '_', name)[:60]


class BaseProvider(ABC):
    """Base class for all AI providers with Codex harvesting support."""
    
    name: str = "base"
    provider_type: str = "unknown"
    config: ProviderConfig = None
    codex: CodexIndex = None
    
    def __init__(self, config: ProviderConfig = None, **kwargs):
        """Initialize the provider."""
        self.config = config or self.get_default_config()
        self.codex = CodexIndex(provider=self.name)
        
        # Override with kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @classmethod
    def get_default_config(cls) -> ProviderConfig:
        """
        Create the default configuration for the provider.
        
        Returns:
        	ProviderConfig: Configuration initialized with the provider name.
        """
        return ProviderConfig(name=cls.name)
    
    @abstractmethod
    def send_message(self, message: str, session_id: str = None, **kwargs) -> str:
        """
        Send a message to the provider and obtain its response.
        
        Parameters:
            message (str): The message to send.
            session_id (str, optional): The session in which to send the message.
            **kwargs: Additional provider-specific options.
        
        Returns:
            str: The provider's response.
        """
        pass
    
    @abstractmethod
    def create_session(self, **kwargs) -> str:
        """
        Create a new provider session.
        
        Returns:
            str: The identifier of the newly created session.
        """
        pass
    
    @abstractmethod
    def get_history(self, session_id: str, **kwargs) -> List[Dict]:
        """
        Retrieve the messages recorded for a session.
        
        Parameters:
        	session_id (str): Identifier of the session whose history to retrieve
        	**kwargs: Provider-specific options
        
        Returns:
        	List[Dict]: The session's messages
        """
        pass
    
    def harvest_code(self, session_id: str, messages: List[Dict] = None, title: str = None) -> List[CodeBlock]:
        """
        Extract and index code blocks from a provider session.
        
        Parameters:
            session_id (str): Identifier of the session to process.
            messages (List[Dict], optional): Session messages to process. If omitted, retrieves the session history.
            title (str, optional): Title associated with the indexed conversation.
        
        Returns:
            List[CodeBlock]: Code blocks extracted from the session.
        """
        if messages is None:
            messages = self.get_history(session_id)
        
        # Index in codex
        self.codex.index_conversation(session_id, title or session_id, messages, self.name)
        
        # Return as CodeBlock objects
        return self.codex.extract_from_messages(messages, session_id, title or session_id, self.name)
    
    def search_code(self, query: str, language: str = None) -> List[Dict]:
        """
        Search this provider's harvested code blocks for a matching term.
        
        Parameters:
            query (str): Term to find in the stored code.
            language (str, optional): Language used to filter results.
        
        Returns:
            List[Dict]: Matching code blocks and their associated metadata.
        """
        return self.codex.search(query, language, self.name)
    
    def get_code_by_hash(self, content_hash: str) -> Optional[str]:
        """
        Retrieve stored code by its content hash.
        
        Parameters:
            content_hash (str): Hash identifying the stored code.
        
        Returns:
            Optional[str]: The code associated with the hash, or `None` if it is unavailable.
        """
        return self.codex.get_code_by_hash(content_hash)
    
    def is_available(self) -> bool:
        """
        Determine whether the provider is available.
        
        Returns:
        	bool: `true` if the provider is available, `false` otherwise.
        """
        return True
    
    def __repr__(self):
        """Return a descriptive representation containing the provider name and type."""
        return f"{self.name} ({self.provider_type})"
