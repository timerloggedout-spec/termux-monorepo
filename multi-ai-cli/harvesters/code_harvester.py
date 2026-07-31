#!/usr/bin/env python3
"""Code Harvester for extracting and collecting code from various sources."""
import os
import json
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Set
from datetime import datetime
from dataclasses import dataclass, field
from rich.console import Console

console = Console()

@dataclass
class CodeSnippet:
    """Represents a harvested code snippet."""
    content: str
    language: str = "unknown"
    source: str = "unknown"
    file_path: str = ""
    line_start: int = 0
    line_end: int = 0
    hash: str = ""
    metadata: Dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __post_init__(self):
        if not self.hash:
            self.hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        """Compute SHA256 hash of content."""
        return hashlib.sha256(self.content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "language": self.language,
            "source": self.source,
            "file_path": self.file_path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "hash": self.hash,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CodeSnippet':
        """Create from dictionary."""
        return cls(**data)

class CodeHarvester:
    """Harvests code from files, directories, and other sources."""
    
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
    
    # Code block patterns for extracting from text
    CODE_BLOCK_PATTERNS = [
        (r'```(\w+)?\n([\s\S]*?)```', 'markdown'),
        (r'```(\w+)?\n([\s\S]*?)```', 'markdown'),
        (r'~~~(\w+)?\n([\s\S]*?)~~~', 'markdown'),
        (r'---\s*\n(\w+):\s*\n([\s\S]*?)---\s*\n', 'yaml'),
    ]
    
    def __init__(self, storage_path: str = None):
        """Initialize the harvester."""
        self.storage_path = storage_path or os.path.join(
            os.path.expanduser("~/.mistralai-cli"), "harvested_code"
        )
        os.makedirs(self.storage_path, exist_ok=True)
        self.snippets: List[CodeSnippet] = []
        self.index: Dict[str, CodeSnippet] = {}
    
    def harvest_file(self, file_path: str, language: str = None) -> List[CodeSnippet]:
        """Harvest code from a single file."""
        path = Path(file_path)
        if not path.exists():
            console.print(f"[red]File not found: {file_path}[/]")
            return []
        
        try:
            content = path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            try:
                content = path.read_text(encoding='latin-1')
            except Exception as e:
                console.print(f"[red]Failed to read {file_path}: {e}[/]")
                return []
        
        # Determine language
        lang = language or self._detect_language(file_path)
        
        # Create snippet
        snippet = CodeSnippet(
            content=content,
            language=lang,
            source="file",
            file_path=str(file_path),
            metadata={
                "file_size": len(content),
                "file_type": "source",
            }
        )
        
        self.snippets.append(snippet)
        self.index[snippet.hash] = snippet
        
        return [snippet]
    
    def harvest_directory(self, dir_path: str, recursive: bool = True, patterns: List[str] = None) -> List[CodeSnippet]:
        """Harvest code from a directory."""
        path = Path(dir_path)
        if not path.exists():
            console.print(f"[red]Directory not found: {dir_path}[/]")
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
                
                # Skip hidden files and common non-code files
                if file.startswith('.'):
                    continue
                if file in ['__pycache__', '.git', '.svn', 'node_modules', 'venv', '.venv']:
                    continue
                
                # Harvest the file
                snippets = self.harvest_file(str(file_path))
                harvested.extend(snippets)
        
        return harvested
    
    def harvest_from_text(self, text: str, source: str = "text") -> List[CodeSnippet]:
        """Extract code blocks from text content."""
        snippets = []
        
        for pattern, lang_type in self.CODE_BLOCK_PATTERNS:
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
            for match in matches:
                lang = match.group(1) or "unknown"
                code = match.group(2).strip()
                
                if code:
                    snippet = CodeSnippet(
                        content=code,
                        language=lang if lang != "unknown" else lang_type,
                        source=source,
                        metadata={
                            "extracted_from": "text",
                            "extraction_method": "regex",
                        }
                    )
                    snippets.append(snippet)
                    self.snippets.append(snippet)
                    self.index[snippet.hash] = snippet
        
        return snippets
    
    def harvest_from_session(self, session_data: List[Dict]) -> List[CodeSnippet]:
        """Harvest code from chat session data."""
        snippets = []
        
        for message in session_data:
            role = message.get("role", "unknown")
            content = message.get("content", "")
            
            # Extract code blocks from message content
            extracted = self.harvest_from_text(content, f"session:{role}")
            snippets.extend(extracted)
        
        return snippets
    
    def _detect_language(self, file_path: str) -> str:
        """Detect language from file extension."""
        ext = Path(file_path).suffix.lower()
        return self.LANGUAGE_EXTENSIONS.get(ext, "unknown")
    
    def save_to_storage(self, name: str = "default") -> str:
        """Save harvested snippets to storage."""
        storage_file = os.path.join(self.storage_path, f"{name}.json")
        data = [s.to_dict() for s in self.snippets]
        
        with open(storage_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        console.print(f"[green]Saved {len(self.snippets)} snippets to {storage_file}[/]")
        return storage_file
    
    def load_from_storage(self, name: str = "default") -> List[CodeSnippet]:
        """Load snippets from storage."""
        storage_file = os.path.join(self.storage_path, f"{name}.json")
        
        if not os.path.exists(storage_file):
            console.print(f"[red]Storage file not found: {storage_file}[/]")
            return []
        
        with open(storage_file) as f:
            data = json.load(f)
        
        self.snippets = [CodeSnippet.from_dict(s) for s in data]
        self.index = {s.hash: s for s in self.snippets}
        
        console.print(f"[green]Loaded {len(self.snippets)} snippets from {storage_file}[/]")
        return self.snippets
    
    def get_snippets_by_language(self, language: str) -> List[CodeSnippet]:
        """Get all snippets of a specific language."""
        return [s for s in self.snippets if s.language.lower() == language.lower()]
    
    def get_snippets_by_source(self, source: str) -> List[CodeSnippet]:
        """Get all snippets from a specific source."""
        return [s for s in self.snippets if s.source == source]
    
    def search_snippets(self, query: str) -> List[CodeSnippet]:
        """Search snippets by content."""
        query_lower = query.lower()
        return [s for s in self.snippets if query_lower in s.content.lower()]
    
    def clear(self):
        """Clear all harvested snippets."""
        self.snippets.clear()
        self.index.clear()

if __name__ == "__main__":
    # Example usage
    harvester = CodeHarvester()
    
    # Harvest from current directory
    snippets = harvester.harvest_directory(".", recursive=False, patterns=['.py'])
    print(f"Harvested {len(snippets)} Python snippets")
    
    # Save to storage
    harvester.save_to_storage("test_harvest")
