#!/usr/bin/env python3
"""Code Extractor for extracting code from various formats.

This uses lightweight regex extraction (not BeautifulSoup) following the
same pattern as the Codex system in cli-synthegration.
"""
import os
import re
import json
import hashlib
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from rich.console import Console

console = Console()

@dataclass
class ExtractedCode:
    """Represents extracted code."""
    content: str
    language: str
    source: str
    start_line: int = 0
    end_line: int = 0
    content_hash: str = ""
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if not self.content_hash and self.content:
            self.content_hash = hashlib.sha256(self.content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "language": self.language,
            "source": self.source,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "content_hash": self.content_hash,
            "metadata": self.metadata,
        }

class CodeExtractor:
    """Extracts code from various formats and sources.
    
    Uses the same lightweight regex pattern as cli-synthegration's Codex:
    r"```(\w+)?\n(.*?)```"
    
    This is intentionally lightweight (no BeautifulSoup) for performance
    and compatibility with the existing DeepSeek workflow.
    """
    
    # Code block pattern (same as Codex)
    CODE_BLOCK_PATTERN = re.compile(r'```(\w+)?\n(.*?)```', re.DOTALL)
    
    # File magic numbers for detection
    MAGIC_NUMBERS = {
        b'#!/usr/bin/env python': 'python',
        b'#!/usr/bin/python': 'python',
        b'<?php': 'php',
        b'<!DOCTYPE html': 'html',
        b'<!--': 'html',
        b'<?xml': 'xml',
    }
    
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
    
    def __init__(self):
        """Initialize the extractor."""
        pass
    
    def extract_from_text(self, text: str, source: str = "text") -> List[ExtractedCode]:
        """Extract code blocks from text using regex.
        
        This is the primary method, using the same pattern as Codex.
        
        Args:
            text: The text to extract code from
            source: Source identifier
            
        Returns:
            List of ExtractedCode objects
        """
        extracted = []
        
        for match in self.CODE_BLOCK_PATTERN.finditer(text):
            lang = (match.group(1) or 'text').lower()
            code = match.group(2).strip()
            
            if code:
                extracted.append(ExtractedCode(
                    content=code,
                    language=lang,
                    source=source,
                    metadata={
                        "extraction_method": "regex",
                        "pattern": "code_block",
                    }
                ))
        
        return extracted
    
    def extract_from_messages(self, messages: List[Dict]) -> List[ExtractedCode]:
        """Extract code blocks from a list of messages.
        
        Args:
            messages: List of message dictionaries with 'content' key
            
        Returns:
            List of ExtractedCode objects
        """
        extracted = []
        
        for msg_idx, msg in enumerate(messages):
            content = msg.get('content', '')
            role = msg.get('role', 'unknown')
            
            for blk_idx, match in enumerate(self.CODE_BLOCK_PATTERN.finditer(content)):
                lang = (match.group(1) or 'text').lower()
                code = match.group(2).strip()
                
                if code:
                    extracted.append(ExtractedCode(
                        content=code,
                        language=lang,
                        source=f"session:{role}",
                        start_line=msg_idx,
                        end_line=msg_idx,
                        metadata={
                            "extraction_method": "regex",
                            "message_index": msg_idx,
                            "block_index": blk_idx,
                            "role": role,
                        }
                    ))
        
        return extracted
    
    def extract_from_file(self, file_path: str) -> List[ExtractedCode]:
        """Extract code from a file.
        
        For markdown files, extracts code blocks.
        For other files, returns the entire file as code.
        
        Args:
            file_path: Path to the file
            
        Returns:
            List of ExtractedCode objects
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
        
        # Detect language
        language = self._detect_language(file_path, content)
        
        # For markdown, extract code blocks
        if language == "markdown":
            return self.extract_from_text(content, file_path)
        
        # For other files, return entire file
        return [ExtractedCode(
            content=content,
            language=language,
            source=file_path,
            metadata={
                "file_type": "source",
                "file_path": file_path,
            }
        )]
    
    def extract_from_json(self, json_data: Dict) -> List[ExtractedCode]:
        """Extract code from JSON data (e.g., API responses).
        
        Args:
            json_data: JSON data to extract from
            
        Returns:
            List of ExtractedCode objects
        """
        extracted = []
        
        # Check for code in common fields
        code_fields = ["code", "content", "text", "message", "response"]
        
        for field in code_fields:
            if field in json_data:
                content = json_data[field]
                if isinstance(content, str):
                    # Extract code blocks from the content
                    extracted.extend(self.extract_from_text(content, f"json:{field}"))
        
        # Recursively check nested structures
        for key, value in json_data.items():
            if isinstance(value, dict):
                extracted.extend(self.extract_from_json(value))
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        extracted.extend(self.extract_from_json(item))
        
        return extracted
    
    def _detect_language(self, file_path: str, content: str = "") -> str:
        """Detect language from file path and content."""
        # First try file extension
        ext = Path(file_path).suffix.lower()
        if ext in self.LANGUAGE_EXTENSIONS:
            return self.LANGUAGE_EXTENSIONS[ext]
        
        # Try magic numbers
        if content:
            for magic, lang in self.MAGIC_NUMBERS.items():
                if isinstance(magic, bytes):
                    if content.encode().startswith(magic):
                        return lang
                else:
                    if content.startswith(magic):
                        return lang
        
        return "text"
    
    def _detect_language_from_content(self, content: str) -> str:
        """Detect language from content only."""
        # Try magic numbers
        for magic, lang in self.MAGIC_NUMBERS.items():
            if isinstance(magic, bytes):
                if content.encode().startswith(magic):
                    return lang
            else:
                if content.startswith(magic):
                    return lang
        
        # Try common patterns
        if re.search(r'def \w+\(', content):
            return "python"
        if re.search(r'function \w+\(', content):
            return "javascript"
        if re.search(r'public class \w+', content):
            return "java"
        if re.search(r'#include <', content):
            return "c"
        if re.search(r'package main', content):
            return "go"
        if re.search(r'<?php', content):
            return "php"
        
        return "text"
    
    def clean_code(self, code: str, language: str) -> str:
        """Clean extracted code (remove comments, normalize, etc.).
        
        Args:
            code: The code to clean
            language: The language of the code
            
        Returns:
            Cleaned code
        """
        if language == "python":
            # Remove docstrings
            code = re.sub(r'"""[\s\S]*?"""', '', code)
            code = re.sub(r"'''[\s\S]*?'''", '', code)
        elif language == "javascript":
            # Remove comments
            code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
            code = re.sub(r'//.*', '', code)
        
        # Normalize whitespace
        code = re.sub(r'\s+', ' ', code)
        code = code.strip()
        
        return code


if __name__ == "__main__":
    # Example usage
    extractor = CodeExtractor()
    
    # Test markdown extraction
    markdown_text = """
    Here's some Python code:
    
    ```python
    def hello():
        print("Hello, World!")
    ```
    
    And some JavaScript:
    
    ```javascript
    function add(a, b) {
        return a + b;
    }
    ```
    """
    
    extracted = extractor.extract_from_text(markdown_text, "test_markdown")
    print(f"Extracted {len(extracted)} code blocks")
    for code in extracted:
        print(f"  - {code.language}: {code.content_hash}")
        print(f"    Content: {code.content[:30]}...")
