#!/usr/bin/env python3
"""Code Extractor for extracting code from various formats."""
import os
import re
import json
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
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "language": self.language,
            "source": self.source,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "metadata": self.metadata,
        }

class CodeExtractor:
    """Extracts code from various formats and sources."""
    
    # Patterns for extracting code blocks
    PATTERNS = {
        "markdown": [
            (r'```(\w+)?\n([\s\S]*?)```', 'markdown_code'),
            (r'~~~(\w+)?\n([\s\S]*?)~~~', 'markdown_code'),
        ],
        "html": [
            (r'<pre[^>]*><code[^>]*>([\s\S]*?)</code></pre>', 'html_code'),
            (r'<code[^>]*>([\s\S]*?)</code>', 'html_code'),
        ],
        "python": [
            (r'"""([\s\S]*?)"""', 'python_docstring'),
            (r"'''([\s\S]*?)'''", 'python_docstring'),
        ],
        "javascript": [
            (r'/\*([\s\S]*?)\*/', 'javascript_comment'),
            (r'//.*', 'javascript_line_comment'),
        ],
    }
    
    # File magic numbers for detection
    MAGIC_NUMBERS = {
        b'#!/usr/bin/env python': 'python',
        b'#!/usr/bin/python': 'python',
        b'<?php': 'php',
        b'<!DOCTYPE html': 'html',
        b'<!--': 'html',
        b'<?xml': 'xml',
    }
    
    def __init__(self):
        """Initialize the extractor."""
        pass
    
    def extract_from_file(self, file_path: str) -> List[ExtractedCode]:
        """Extract code from a file."""
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
        
        # Detect language from file extension or content
        language = self._detect_language(file_path, content)
        
        # Extract code blocks based on language
        extracted = []
        
        if language == "markdown":
            extracted.extend(self._extract_markdown_code(content, file_path))
        elif language == "html":
            extracted.extend(self._extract_html_code(content, file_path))
        else:
            # For most languages, just return the entire file as code
            extracted.append(ExtractedCode(
                content=content,
                language=language,
                source=file_path,
                metadata={"file_type": "source"}
            ))
        
        return extracted
    
    def extract_from_text(self, text: str, source: str = "text") -> List[ExtractedCode]:
        """Extract code blocks from text."""
        extracted = []
        
        # Try markdown patterns
        for pattern, pattern_type in self.PATTERNS.get("markdown", []):
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
            for match in matches:
                lang = match.group(1) or "unknown"
                code = match.group(2).strip()
                
                if code:
                    extracted.append(ExtractedCode(
                        content=code,
                        language=lang,
                        source=source,
                        metadata={"extraction_method": "regex", "pattern_type": pattern_type}
                    ))
        
        # Try HTML patterns
        for pattern, pattern_type in self.PATTERNS.get("html", []):
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
            for match in matches:
                code = match.group(1).strip()
                
                if code:
                    # Try to detect language from code content
                    lang = self._detect_language_from_content(code)
                    extracted.append(ExtractedCode(
                        content=code,
                        language=lang,
                        source=source,
                        metadata={"extraction_method": "regex", "pattern_type": pattern_type}
                    ))
        
        return extracted
    
    def extract_from_json(self, json_data: Dict) -> List[ExtractedCode]:
        """Extract code from JSON data (e.g., API responses)."""
        extracted = []
        
        # Check for code in common fields
        code_fields = ["code", "content", "text", "message", "response"]
        
        for field in code_fields:
            if field in json_data:
                content = json_data[field]
                if isinstance(content, str):
                    # Try to detect language
                    lang = self._detect_language_from_content(content)
                    extracted.append(ExtractedCode(
                        content=content,
                        language=lang,
                        source="json",
                        metadata={"field": field}
                    ))
        
        # Recursively check nested structures
        for key, value in json_data.items():
            if isinstance(value, dict):
                extracted.extend(self.extract_from_json(value))
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        extracted.extend(self.extract_from_json(item))
        
        return extracted
    
    def extract_from_session(self, session_data: List[Dict]) -> List[ExtractedCode]:
        """Extract code from chat session data."""
        extracted = []
        
        for message in session_data:
            role = message.get("role", "unknown")
            content = message.get("content", "")
            
            # Extract code blocks from message content
            message_extracted = self.extract_from_text(content, f"session:{role}")
            extracted.extend(message_extracted)
        
        return extracted
    
    def _extract_markdown_code(self, content: str, source: str) -> List[ExtractedCode]:
        """Extract code blocks from markdown."""
        extracted = []
        
        # Extract fenced code blocks
        pattern = r'```(\w+)?\n([\s\S]*?)```'
        matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            lang = match.group(1) or "unknown"
            code = match.group(2).strip()
            
            if code:
                extracted.append(ExtractedCode(
                    content=code,
                    language=lang,
                    source=source,
                    metadata={"extraction_method": "markdown_fenced"}
                ))
        
        return extracted
    
    def _extract_html_code(self, content: str, source: str) -> List[ExtractedCode]:
        """Extract code blocks from HTML."""
        extracted = []
        
        # Extract <pre><code> blocks
        pattern = r'<pre[^>]*><code[^>]*>([\s\S]*?)</code></pre>'
        matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            code = match.group(1).strip()
            
            if code:
                # Try to detect language from class attribute
                lang = "unknown"
                # Look for class="language-xxx" in the code tag
                code_match = re.search(r'<code[^>]*class="[^"]*language-(\w+)[^"]*"', match.group(0))
                if code_match:
                    lang = code_match.group(1)
                
                extracted.append(ExtractedCode(
                    content=code,
                    language=lang,
                    source=source,
                    metadata={"extraction_method": "html_pre_code"}
                ))
        
        return extracted
    
    def _detect_language(self, file_path: str, content: str = "") -> str:
        """Detect language from file path and content."""
        # First try file extension
        ext = Path(file_path).suffix.lower()
        
        language_map = {
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
            '.txt': 'text',
        }
        
        if ext in language_map:
            return language_map[ext]
        
        # Try magic numbers
        if content:
            for magic, lang in self.MAGIC_NUMBERS.items():
                if content.startswith(magic.decode() if isinstance(magic, bytes) else magic):
                    return lang
        
        return "unknown"
    
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
        
        return "unknown"
    
    def clean_code(self, code: str, language: str) -> str:
        """Clean extracted code (remove comments, normalize, etc.)."""
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
        print(f"  - {code.language}: {code.content[:30]}...")
