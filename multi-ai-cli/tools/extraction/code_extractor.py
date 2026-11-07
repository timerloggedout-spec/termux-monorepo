#!/usr/bin/env python3
"""Code Extractor - Extract code blocks from text.

This module provides functionality to:
- Extract code blocks from text (Markdown, HTML, plain text)
- Identify programming languages
- Clean and format extracted code
- Handle various code fence formats
"""

import os
import sys
import json
import re
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Generator, Tuple
from dataclasses import dataclass, field


@dataclass
class ExtractedCode:
    """Represents extracted code with metadata."""
    code: str
    language: Optional[str] = None
    source: str = ""
    start_line: int = 0
    end_line: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "language": self.language,
            "source": self.source,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "metadata": self.metadata,
        }


class CodeExtractor:
    """Extract code blocks from text.
    
    This extractor can handle:
    - Markdown code fences (```python, ~~~python, etc.)
    - HTML <pre><code> blocks
    - Indented code blocks
    - Plain text code
    """
    
    # Language aliases
    LANGUAGE_ALIASES = {
        "py": "python",
        "python": "python",
        "js": "javascript",
        "javascript": "javascript",
        "ts": "typescript",
        "typescript": "typescript",
        "java": "java",
        "c": "c",
        "cpp": "cpp",
        "c++": "cpp",
        "c#": "csharp",
        "csharp": "csharp",
        "go": "go",
        "golang": "go",
        "rs": "rust",
        "rust": "rust",
        "rb": "ruby",
        "ruby": "ruby",
        "php": "php",
        "swift": "swift",
        "kt": "kotlin",
        "kotlin": "kotlin",
        "scala": "scala",
        "sh": "bash",
        "bash": "bash",
        "zsh": "bash",
        "shell": "bash",
        "ps1": "powershell",
        "powershell": "powershell",
        "lua": "lua",
        "pl": "perl",
        "perl": "perl",
        "r": "r",
        "jl": "julia",
        "julia": "julia",
        "sql": "sql",
        "html": "html",
        "xml": "xml",
        "json": "json",
        "yaml": "yaml",
        "yml": "yaml",
        "toml": "toml",
        "ini": "ini",
        "cfg": "ini",
        "conf": "ini",
        "makefile": "makefile",
        "dockerfile": "dockerfile",
        "cmake": "cmake",
    }
    
    # Code fence patterns
    CODE_FENCE_PATTERNS = [
        (r"```(\w*)\n([\s\S]*?)```", "markdown_backtick"),
        (r"~~~(\w*)\n([\s\S]*?)~~~", "markdown_tilde"),
        (r"<pre><code class=\"language-(\w*)\">([\s\S]*?)</code></pre>", "html_pre"),
        (r"<code class=\"language-(\w*)\">([\s\S]*?)</code>", "html_code"),
        (r"<pre>([\s\S]*?)</pre>", "html_pre_simple"),
    ]
    
    # Indented code pattern
    INDENTED_CODE_PATTERN = re.compile(r"^ {4}[^\n]+", re.MULTILINE)
    
    def __init__(
        self,
        include_metadata: bool = True,
        clean_code: bool = True,
        preserve_indentation: bool = False,
        **kwargs
    ):
        """Initialize code extractor.
        
        Args:
            include_metadata: Whether to include metadata in results
            clean_code: Whether to clean extracted code
            preserve_indentation: Whether to preserve original indentation
        """
        self.include_metadata = include_metadata
        self.clean_code = clean_code
        self.preserve_indentation = preserve_indentation
    
    def extract(
        self,
        text: str,
        source: str = "",
    ) -> List[ExtractedCode]:
        """Extract code blocks from text.
        
        Args:
            text: Text to extract code from
            source: Source identifier
            
        Returns:
            List of ExtractedCode objects
        """
        results = []
        
        # Extract using patterns
        for pattern, pattern_name in self.CODE_FENCE_PATTERNS:
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
            for match in matches:
                lang = match.group(1).strip().lower()
                code = match.group(2).strip()
                
                # Normalize language
                lang = self.LANGUAGE_ALIASES.get(lang, lang) if lang else None
                
                # Clean code
                if self.clean_code:
                    code = self._clean_code(code, lang)
                
                results.append(ExtractedCode(
                    code=code,
                    language=lang,
                    source=source,
                    metadata={"pattern": pattern_name, "extracted_from": pattern_name}
                ))
        
        # Extract indented code blocks
        if self._has_indented_blocks(text):
            indented_blocks = self._extract_indented_blocks(text)
            for block in indented_blocks:
                results.append(ExtractedCode(
                    code=block,
                    language=None,
                    source=source,
                    metadata={"pattern": "indented", "extracted_from": "indented"}
                ))
        
        # Sort by position
        results.sort(key=lambda x: (x.start_line, x.end_line))
        
        return results
    
    def _has_indented_blocks(self, text: str) -> bool:
        """Check if text has indented code blocks."""
        # Look for lines starting with 4+ spaces
        for line in text.splitlines():
            if line.startswith("    ") and line.strip():
                return True
        return False
    
    def _extract_indented_blocks(self, text: str) -> List[str]:
        """Extract indented code blocks."""
        blocks = []
        current_block = []
        in_block = False
        
        for line in text.splitlines():
            if line.startswith("    ") and line.strip():
                if not in_block:
                    in_block = True
                    current_block = []
                current_block.append(line[4:] if not self.preserve_indentation else line)
            else:
                if in_block and current_block:
                    blocks.append("\n".join(current_block))
                    current_block = []
                in_block = False
        
        # Add last block
        if in_block and current_block:
            blocks.append("\n".join(current_block))
        
        return blocks
    
    def _clean_code(self, code: str, language: Optional[str] = None) -> str:
        """Clean extracted code.
        
        Args:
            code: Code to clean
            language: Language of the code
            
        Returns:
            Cleaned code
        """
        # Remove leading/trailing whitespace
        code = code.strip()
        
        # Remove common artifacts
        code = code.replace("\r\n", "\n")
        code = code.replace("\r", "\n")
        
        # Remove trailing whitespace from each line
        lines = code.splitlines()
        cleaned_lines = []
        for line in lines:
            cleaned = line.rstrip()
            if cleaned or cleaned_lines:
                cleaned_lines.append(cleaned)
        
        code = "\n".join(cleaned_lines)
        
        # Language-specific cleaning
        if language:
            code = self._clean_language_specific(code, language)
        
        return code
    
    def _clean_language_specific(self, code: str, language: str) -> str:
        """Apply language-specific cleaning.
        
        Args:
            code: Code to clean
            language: Language of the code
            
        Returns:
            Cleaned code
        """
        if language in ("python", "py"):
            # Remove Python prompt artifacts
            code = re.sub(r"^>>> ", "", code, flags=re.MULTILINE)
            code = re.sub(r"^\.\.\. ", "", code, flags=re.MULTILINE)
            
            # Remove IPython artifacts
            code = re.sub(r"^In \[[0-9]+\]: ", "", code, flags=re.MULTILINE)
            code = re.sub(r"^Out\[[0-9]+\]: ", "", code, flags=re.MULTILINE)
            
            # Remove Jupyter artifacts
            code = re.sub(r'^# In\[\d+\]:\s*$', "", code, flags=re.MULTILINE)
            code = re.sub(r'^# Out\[\d+\]:\s*$', "", code, flags=re.MULTILINE)
        
        elif language in ("javascript", "js", "typescript", "ts"):
            # Remove Node.js prompt artifacts
            code = re.sub(r"^> ", "", code, flags=re.MULTILINE)
        
        elif language in ("bash", "sh", "zsh", "shell"):
            # Remove shell prompt artifacts
            code = re.sub(r"^\$ ", "", code, flags=re.MULTILINE)
            code = re.sub(r"^# ", "", code, flags=re.MULTILINE)
        
        return code
    
    def extract_from_file(
        self,
        path: Union[str, Path],
        encoding: str = "utf-8",
    ) -> List[ExtractedCode]:
        """Extract code from a file.
        
        Args:
            path: Path to file
            encoding: File encoding
            
        Returns:
            List of ExtractedCode objects
        """
        try:
            content = Path(path).read_text(encoding=encoding)
            return self.extract(content, source=str(path))
        except Exception as e:
            print(f"Error reading file {path}: {e}", file=sys.stderr)
            return []
    
    def extract_from_files(
        self,
        paths: List[Union[str, Path]],
        encoding: str = "utf-8",
    ) -> List[ExtractedCode]:
        """Extract code from multiple files.
        
        Args:
            paths: List of file paths
            encoding: File encoding
            
        Returns:
            List of ExtractedCode objects
        """
        all_results = []
        for path in paths:
            results = self.extract_from_file(path, encoding)
            all_results.extend(results)
        return all_results
    
    def extract_to_dict(
        self,
        text: str,
        source: str = "",
    ) -> List[Dict[str, Any]]:
        """Extract code and return as list of dictionaries.
        
        Args:
            text: Text to extract from
            source: Source identifier
            
        Returns:
            List of code dictionaries
        """
        return [c.to_dict() for c in self.extract(text, source)]
    
    def extract_to_json(
        self,
        text: str,
        source: str = "",
    ) -> str:
        """Extract code and return as JSON.
        
        Args:
            text: Text to extract from
            source: Source identifier
            
        Returns:
            JSON string
        """
        return json.dumps(self.extract_to_dict(text, source), indent=2)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "CodeExtractor",
    "ExtractedCode",
]
