#!/usr/bin/env python3
"""Pattern Extractor - Extract data using regex and string patterns.

This module provides functionality to:
- Extract data using regular expressions
- Extract structured data using patterns
- Extract tables and lists
- Extract key-value pairs
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
class ExtractedPattern:
    """Represents an extracted pattern match."""
    pattern: str
    match: str
    groups: Dict[str, str] = field(default_factory=dict)
    start: int = 0
    end: int = 0
    line: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern": self.pattern,
            "match": self.match,
            "groups": self.groups,
            "start": self.start,
            "end": self.end,
            "line": self.line,
            "metadata": self.metadata,
        }


class PatternExtractor:
    """Extract data using patterns.
    
    This extractor can handle:
    - Regular expressions
    - String patterns
    - Template patterns
    - Multi-line patterns
    """
    
    # Common patterns
    COMMON_PATTERNS = {
        "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "url": r"https?://[^\s]+",
        "phone": r"\+?[0-9\s\-\(\)]{10,}",
        "date_iso": r"\d{4}-\d{2}-\d{2}",
        "date_us": r"\d{1,2}/\d{1,2}/\d{2,4}",
        "time": r"\d{1,2}:\d{2}(:\d{2})?",
        "uuid": r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
        "ipv4": r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
        "ipv6": r"[0-9a-fA-F:]+:+[0-9a-fA-F]+",
        "number": r"-?\d+\.?\d*",
        "hex": r"0x[0-9a-fA-F]+",
        "binary": r"0b[01]+",
        "octal": r"0o[0-7]+",
    }
    
    # Code-specific patterns
    CODE_PATTERNS = {
        "function_def": r"def\s+(\w+)\s*\(([^)]*)\)\s*:",
        "class_def": r"class\s+(\w+)\s*(\([^)]*\))?\s*:",
        "import": r"^(import|from)\s+([^\s]+)\s*(import\s+([^\s]+))?",
        "variable": r"(\w+)\s*=\s*[^=]+",
        "comment": r"#\s*(.+)$",
        "docstring": r'"""(.+?)"""',
        "decorator": r"@(\w+)",
    }
    
    def __init__(
        self,
        patterns: Optional[Dict[str, str]] = None,
        case_sensitive: bool = False,
        multiline: bool = True,
        dotall: bool = True,
        **kwargs
    ):
        """Initialize pattern extractor.
        
        Args:
            patterns: Custom patterns to use
            case_sensitive: Whether patterns are case-sensitive
            multiline: Whether to use multiline matching
            dotall: Whether . matches newline
        """
        self.patterns = patterns or {}
        self.case_sensitive = case_sensitive
        self.multiline = multiline
        self.dotall = dotall
        self._compiled_patterns = {}
    
    def _compile_pattern(self, pattern: str) -> re.Pattern:
        """Compile a regex pattern.
        
        Args:
            pattern: Regex pattern string
            
        Returns:
            Compiled regex pattern
        """
        flags = 0
        if not self.case_sensitive:
            flags |= re.IGNORECASE
        if self.multiline:
            flags |= re.MULTILINE
        if self.dotall:
            flags |= re.DOTALL
        
        return re.compile(pattern, flags)
    
    def _get_compiled_pattern(self, pattern: str) -> re.Pattern:
        """Get compiled pattern, compiling if necessary.
        
        Args:
            pattern: Pattern string
            
        Returns:
            Compiled pattern
        """
        if pattern not in self._compiled_patterns:
            self._compiled_patterns[pattern] = self._compile_pattern(pattern)
        return self._compiled_patterns[pattern]
    
    def extract(
        self,
        text: str,
        pattern: Optional[str] = None,
        pattern_name: Optional[str] = None,
        group_names: Optional[List[str]] = None,
    ) -> List[ExtractedPattern]:
        """Extract matches for a pattern.
        
        Args:
            text: Text to extract from
            pattern: Pattern to use (uses pattern_name if not specified)
            pattern_name: Name of predefined pattern
            group_names: Names for capture groups
            
        Returns:
            List of ExtractedPattern objects
        """
        # Get pattern
        if pattern is None:
            if pattern_name:
                pattern = self.patterns.get(pattern_name) or self.COMMON_PATTERNS.get(pattern_name)
            if pattern is None:
                raise ValueError("No pattern specified")
        
        # Compile pattern
        compiled = self._get_compiled_pattern(pattern)
        
        # Find all matches
        results = []
        for match in compiled.finditer(text):
            groups = {}
            if group_names:
                for i, name in enumerate(group_names):
                    if i < len(match.groups()):
                        groups[name] = match.group(i + 1)
            else:
                for i, group in enumerate(match.groups()):
                    groups[f"group_{i}"] = group
            
            # Count newlines before match to get line number
            line = text[:match.start()].count("\n") + 1
            
            results.append(ExtractedPattern(
                pattern=pattern,
                match=match.group(0),
                groups=groups,
                start=match.start(),
                end=match.end(),
                line=line,
                metadata={
                    "pattern_name": pattern_name,
                    "all_groups": match.groups(),
                }
            ))
        
        return results
    
    def extract_all(
        self,
        text: str,
        pattern_names: Optional[List[str]] = None,
    ) -> Dict[str, List[ExtractedPattern]]:
        """Extract matches for all specified patterns.
        
        Args:
            text: Text to extract from
            pattern_names: List of pattern names to use
            
        Returns:
            Dictionary mapping pattern names to lists of matches
        """
        if pattern_names is None:
            pattern_names = list(self.patterns.keys()) + list(self.COMMON_PATTERNS.keys())
        
        results = {}
        for name in pattern_names:
            matches = self.extract(text, pattern_name=name)
            if matches:
                results[name] = matches
        
        return results
    
    def extract_table(
        self,
        text: str,
        header_pattern: Optional[str] = None,
        row_pattern: Optional[str] = None,
        delimiter: str = "\t",
    ) -> List[Dict[str, str]]:
        """Extract table data.
        
        Args:
            text: Text to extract from
            header_pattern: Pattern to match header row
            row_pattern: Pattern to match data rows
            delimiter: Column delimiter
            
        Returns:
            List of row dictionaries
        """
        lines = text.splitlines()
        
        # Find header
        headers = []
        data_start = 0
        
        if header_pattern:
            compiled = self._get_compiled_pattern(header_pattern)
            for i, line in enumerate(lines):
                match = compiled.match(line)
                if match:
                    headers = line.split(delimiter)
                    data_start = i + 1
                    break
        else:
            # Use first line as header
            if lines:
                headers = lines[0].split(delimiter)
                data_start = 1
        
        # Extract rows
        rows = []
        for line in lines[data_start:]:
            if not line.strip():
                continue
            
            values = line.split(delimiter)
            if len(values) != len(headers):
                continue
            
            row = {}
            for header, value in zip(headers, values):
                row[header.strip()] = value.strip()
            rows.append(row)
        
        return rows
    
    def extract_list(
        self,
        text: str,
        item_pattern: str,
        prefix: Optional[str] = None,
    ) -> List[str]:
        """Extract list items.
        
        Args:
            text: Text to extract from
            item_pattern: Pattern to match list items
            prefix: Prefix to strip from items
            
        Returns:
            List of extracted items
        """
        matches = self.extract(text, pattern=item_pattern)
        items = [m.match for m in matches]
        
        if prefix:
            items = [item[len(prefix):] if item.startswith(prefix) else item for item in items]
        
        return items
    
    def extract_key_value(
        self,
        text: str,
        key_pattern: Optional[str] = None,
        value_pattern: Optional[str] = None,
        delimiter: str = ":",
    ) -> Dict[str, str]:
        """Extract key-value pairs.
        
        Args:
            text: Text to extract from
            key_pattern: Pattern to match keys
            value_pattern: Pattern to match values
            delimiter: Key-value delimiter
            
        Returns:
            Dictionary of key-value pairs
        """
        pairs = {}
        
        # Split by lines
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("//"):
                continue
            
            # Split by delimiter
            if delimiter in line:
                key, value = line.split(delimiter, 1)
                pairs[key.strip()] = value.strip()
            
            # Try regex patterns
            elif key_pattern and value_pattern:
                key_compiled = self._get_compiled_pattern(key_pattern)
                value_compiled = self._get_compiled_pattern(value_pattern)
                
                key_match = key_compiled.match(line)
                if key_match:
                    key = key_match.group(0)
                    remaining = line[len(key):]
                    value_match = value_compiled.match(remaining)
                    if value_match:
                        pairs[key] = value_match.group(0)
        
        return pairs
    
    def extract_to_dict(
        self,
        text: str,
        pattern: Optional[str] = None,
        pattern_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Extract and return as list of dictionaries.
        
        Args:
            text: Text to extract from
            pattern: Pattern to use
            pattern_name: Name of predefined pattern
            
        Returns:
            List of match dictionaries
        """
        return [m.to_dict() for m in self.extract(text, pattern, pattern_name)]
    
    def extract_to_json(
        self,
        text: str,
        pattern: Optional[str] = None,
        pattern_name: Optional[str] = None,
    ) -> str:
        """Extract and return as JSON.
        
        Args:
            text: Text to extract from
            pattern: Pattern to use
            pattern_name: Name of predefined pattern
            
        Returns:
            JSON string
        """
        return json.dumps(self.extract_to_dict(text, pattern, pattern_name), indent=2)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "PatternExtractor",
    "ExtractedPattern",
]
