"""
Code Harvester Module for Multi-AI CLI

This module provides comprehensive code harvesting and extraction
capabilities, integrating with various sources including:
- GitHub repositories via gh CLI
- Local filesystems
- Remote Termux devices via Pinggy bridge
- Web-based AI service responses

Architecture:
- Uses the DeepTermWebWrapper for remote access
- Supports multiple extraction strategies
- Provides code indexing and search capabilities
- Maintains security boundaries
"""

import os
import sys
import json
import re
import base64
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List, Set
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from core.core import DeepTermWebWrapper, get_wrapper, SecurityConfig


@dataclass
class CodeBlock:
    """Represents an extracted code block"""
    language: str
    code: str
    source: str
    file_path: Optional[str] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "language": self.language,
            "code": self.code,
            "source": self.source,
            "file_path": self.file_path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "metadata": self.metadata
        }


@dataclass
class HarvestResult:
    """Result of a harvest operation"""
    success: bool
    code_blocks: List[CodeBlock] = field(default_factory=list)
    files_processed: int = 0
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "success": self.success,
            "code_blocks": [cb.to_dict() for cb in self.code_blocks],
            "files_processed": self.files_processed,
            "errors": self.errors,
            "metadata": self.metadata
        }


class CodeExtractor(ABC):
    """Abstract base class for code extractors"""
    
    @abstractmethod
    def extract(self, content: str, file_path: Optional[str] = None) -> List[CodeBlock]:
        """Extract code blocks from content"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get the name of this extractor"""
        pass


class MarkdownCodeExtractor(CodeExtractor):
    """Extract code from Markdown-formatted text"""
    
    def __init__(self):
        # Pattern for markdown code blocks: ```language
        self.code_pattern = re.compile(
            r'```(\w*)\n([\s\S]*?)```',
            re.MULTILINE | re.DOTALL
        )
        # Pattern for inline code: `code`
        self.inline_pattern = re.compile(r'`([^`\n]+)`')
    
    def get_name(self) -> str:
        return "markdown"
    
    def extract(self, content: str, file_path: Optional[str] = None) -> List[CodeBlock]:
        code_blocks = []
        source = file_path or "text"
        
        # Extract block code
        for match in self.code_pattern.finditer(content):
            lang = match.group(1).strip() if match.group(1).strip() else "text"
            code = match.group(2).strip()
            
            # Clean up code
            code = self._clean_code(code)
            
            code_blocks.append(CodeBlock(
                language=lang,
                code=code,
                source=source,
                file_path=file_path,
                metadata={"extractor": self.get_name()}
            ))
        
        # Extract inline code
        for match in self.inline_pattern.finditer(content):
            code = match.group(1).strip()
            code_blocks.append(CodeBlock(
                language="text",
                code=code,
                source=source,
                file_path=file_path,
                metadata={"extractor": self.get_name(), "type": "inline"}
            ))
        
        return code_blocks
    
    def _clean_code(self, code: str) -> str:
        """Clean extracted code"""
        # Remove leading/trailing whitespace
        code = code.strip()
        # Normalize line endings
        code = code.replace('\r\n', '\n').replace('\r', '\n')
        return code


class PythonCodeExtractor(CodeExtractor):
    """Extract Python-specific code patterns"""
    
    def get_name(self) -> str:
        return "python"
    
    def extract(self, content: str, file_path: Optional[str] = None) -> List[CodeBlock]:
        code_blocks = []
        source = file_path or "text"
        
        # Extract Python code blocks
        python_blocks = []
        
        # Pattern for Python code blocks
        python_pattern = re.compile(
            r'```python\n([\s\S]*?)```',
            re.MULTILINE | re.DOTALL
        )
        
        for match in python_pattern.finditer(content):
            code = match.group(1).strip()
            python_blocks.append(CodeBlock(
                language="python",
                code=code,
                source=source,
                file_path=file_path,
                metadata={"extractor": self.get_name()}
            ))
        
        # If no Python blocks found, try to detect Python code
        if not python_blocks:
            # Look for Python-specific patterns
            python_keywords = ['def ', 'class ', 'import ', 'from ', 'async ', 
                             'lambda ', 'try:', 'except:', 'if __name__']
            
            for keyword in python_keywords:
                if keyword in content:
                    # Extract the entire content as Python
                    code_blocks.append(CodeBlock(
                        language="python",
                        code=content.strip(),
                        source=source,
                        file_path=file_path,
                        metadata={"extractor": self.get_name(), "detected": True}
                    ))
                    break
        else:
            code_blocks.extend(python_blocks)
        
        return code_blocks


class JSONCodeExtractor(CodeExtractor):
    """Extract code from JSON data"""
    
    def get_name(self) -> str:
        return "json"
    
    def extract(self, content: str, file_path: Optional[str] = None) -> List[CodeBlock]:
        code_blocks = []
        source = file_path or "text"
        
        try:
            data = json.loads(content)
            
            # Extract code from JSON fields
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, str) and self._is_code(value):
                        code_blocks.append(CodeBlock(
                            language=self._detect_language(value),
                            code=value,
                            source=source,
                            file_path=file_path,
                            metadata={"extractor": self.get_name(), "json_key": key}
                        ))
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    if isinstance(item, str) and self._is_code(item):
                        code_blocks.append(CodeBlock(
                            language=self._detect_language(item),
                            code=item,
                            source=source,
                            file_path=file_path,
                            metadata={"extractor": self.get_name(), "json_index": i}
                        ))
        except json.JSONDecodeError:
            pass
        
        return code_blocks
    
    def _is_code(self, text: str) -> bool:
        """Check if text looks like code"""
        # Simple heuristic: contains common code patterns
        code_patterns = ['def ', 'class ', 'function', 'import ', 'from ', 
                        'const ', 'let ', 'var ', 'return ', 'if (', 'for (']
        return any(pattern in text for pattern in code_patterns)
    
    def _detect_language(self, code: str) -> str:
        """Detect language from code"""
        if 'def ' in code and ':' in code:
            return 'python'
        elif 'function' in code and '{' in code:
            return 'javascript'
        elif 'const ' in code or 'let ' in code:
            return 'javascript'
        elif 'import ' in code and ';' in code:
            return 'java'
        return 'text'


class CompositeCodeExtractor(CodeExtractor):
    """Composite extractor that uses multiple strategies"""
    
    def __init__(self):
        self.extractors = [
            MarkdownCodeExtractor(),
            PythonCodeExtractor(),
            JSONCodeExtractor()
        ]
    
    def get_name(self) -> str:
        return "composite"
    
    def extract(self, content: str, file_path: Optional[str] = None) -> List[CodeBlock]:
        all_blocks = []
        
        for extractor in self.extractors:
            try:
                blocks = extractor.extract(content, file_path)
                all_blocks.extend(blocks)
            except Exception as e:
                print(f"Warning: Extractor {extractor.get_name()} failed: {e}", 
                      file=sys.stderr)
        
        # Deduplicate blocks with same content
        seen = set()
        unique_blocks = []
        for block in all_blocks:
            content_hash = hash(block.code)
            if content_hash not in seen:
                seen.add(content_hash)
                unique_blocks.append(block)
        
        return unique_blocks


class CodeHarvester:
    """
    Main code harvester class
    
    Provides comprehensive code harvesting from multiple sources
    with support for extraction, indexing, and search.
    """
    
    def __init__(self, wrapper: Optional[DeepTermWebWrapper] = None,
                 security_config: Optional[SecurityConfig] = None):
        self.wrapper = wrapper or get_wrapper()
        self.security = security_config or SecurityConfig()
        self.extractor = CompositeCodeExtractor()
        self._index: Dict[str, CodeBlock] = {}
        self._harvested_files: Set[str] = set()
    
    def harvest_from_text(self, text: str, 
                         source: str = "text") -> HarvestResult:
        """Harvest code from plain text"""
        try:
            code_blocks = self.extractor.extract(text, None)
            
            for block in code_blocks:
                block.source = source
                block.metadata["harvest_method"] = "text"
                self._index_code(block)
            
            return HarvestResult(
                success=True,
                code_blocks=code_blocks,
                files_processed=1,
                metadata={"source": source, "method": "text"}
            )
        except Exception as e:
            return HarvestResult(
                success=False,
                errors=[str(e)],
                metadata={"source": source, "method": "text"}
            )
    
    def harvest_from_file(self, file_path: str) -> HarvestResult:
        """Harvest code from a local file"""
        result = HarvestResult(
            success=False,
            metadata={"method": "file", "path": file_path}
        )
        
        # Security check
        if not self.security.validate_path(file_path):
            result.errors.append(f"Path outside sandbox: {file_path}")
            return result
        
        path_obj = Path(file_path)
        
        # Check if already harvested
        if str(path_obj) in self._harvested_files:
            result.success = True
            result.metadata["cached"] = True
            return result
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            code_blocks = self.extractor.extract(content, str(path_obj))
            
            for block in code_blocks:
                block.source = str(path_obj)
                block.metadata["harvest_method"] = "file"
                self._index_code(block)
            
            self._harvested_files.add(str(path_obj))
            result.success = True
            result.code_blocks = code_blocks
            result.files_processed = 1
            
        except Exception as e:
            result.errors.append(str(e))
        
        return result
    
    def harvest_from_github(self, repo: str, 
                           path: str = "",
                           branch: str = "master",
                           recursive: bool = False) -> HarvestResult:
        """Harvest code from GitHub repository"""
        result = HarvestResult(
            success=False,
            metadata={"method": "github", "repo": repo, "path": path, "branch": branch}
        )
        
        try:
            # Use gh CLI to get repository contents
            cmd = [
                "gh", "api",
                f"repos/{repo}/contents/{path}?ref={branch}",
                "--jq", ".[].path"
            ]
            
            proc = subprocess.run(cmd, capture_output=True, 
                                timeout=60, text=True)
            
            if proc.returncode != 0:
                result.errors.append(f"gh CLI error: {proc.stderr}")
                return result
            
            files = [f.strip() for f in proc.stdout.split('\n') if f.strip()]
            
            for file_path in files:
                if not file_path:
                    continue
                
                # Get file content
                content_cmd = [
                    "gh", "api",
                    f"repos/{repo}/contents/{file_path}?ref={branch}",
                    "--jq", ".content"
                ]
                
                content_proc = subprocess.run(content_cmd, capture_output=True,
                                            timeout=30, text=True)
                
                if content_proc.returncode == 0:
                    encoded = content_proc.stdout.strip()
                    if encoded:
                        try:
                            content = base64.b64decode(encoded).decode('utf-8')
                            code_blocks = self.extractor.extract(content, file_path)
                            
                            for block in code_blocks:
                                block.source = f"github:{repo}@{branch}"
                                block.file_path = file_path
                                block.metadata["harvest_method"] = "github"
                                block.metadata["repo"] = repo
                                block.metadata["branch"] = branch
                                self._index_code(block)
                            
                            result.code_blocks.extend(code_blocks)
                            result.files_processed += 1
                            
                        except (base64.binascii.Error, UnicodeDecodeError) as e:
                            result.errors.append(f"Failed to decode {file_path}: {e}")
                
                # If recursive and this is a directory, recurse
                if recursive:
                    dir_cmd = [
                        "gh", "api",
                        f"repos/{repo}/contents/{file_path}?ref={branch}",
                        "--jq", ".type"
                    ]
                    dir_proc = subprocess.run(dir_cmd, capture_output=True,
                                           timeout=10, text=True)
                    if dir_proc.returncode == 0 and dir_proc.stdout.strip() == '"dir"':
                        sub_result = self.harvest_from_github(
                            repo, file_path, branch, recursive
                        )
                        result.code_blocks.extend(sub_result.code_blocks)
                        result.files_processed += sub_result.files_processed
                        result.errors.extend(sub_result.errors)
            
            result.success = len(result.code_blocks) > 0 or len(result.errors) == 0
            
        except Exception as e:
            result.errors.append(str(e))
        
        return result
    
    def harvest_from_termux(self, remote_path: str, 
                           ssh_key_path: Optional[str] = None) -> HarvestResult:
        """Harvest code from remote Termux device via bridge"""
        result = HarvestResult(
            success=False,
            metadata={"method": "termux", "path": remote_path}
        )
        
        try:
            # Execute remote command to read file
            command = f"cat {remote_path}"
            content = self.wrapper.execute_shell_command(command, ssh_key_path)
            
            # Extract code from content
            code_blocks = self.extractor.extract(content, remote_path)
            
            for block in code_blocks:
                block.source = f"termux:{remote_path}"
                block.metadata["harvest_method"] = "termux"
                self._index_code(block)
            
            result.success = True
            result.code_blocks = code_blocks
            result.files_processed = 1
            
        except Exception as e:
            result.errors.append(str(e))
        
        return result
    
    def harvest_from_directory(self, directory: str, 
                              recursive: bool = True) -> HarvestResult:
        """Harvest code from a local directory"""
        result = HarvestResult(
            success=False,
            metadata={"method": "directory", "path": directory}
        )
        
        # Security check
        if not self.security.validate_path(directory):
            result.errors.append(f"Directory outside sandbox: {directory}")
            return result
        
        path_obj = Path(directory)
        
        try:
            for item in path_obj.iterdir():
                if item.is_file():
                    file_result = self.harvest_from_file(str(item))
                    result.code_blocks.extend(file_result.code_blocks)
                    result.files_processed += file_result.files_processed
                    result.errors.extend(file_result.errors)
                elif item.is_dir() and recursive:
                    sub_result = self.harvest_from_directory(str(item), recursive)
                    result.code_blocks.extend(sub_result.code_blocks)
                    result.files_processed += sub_result.files_processed
                    result.errors.extend(sub_result.errors)
            
            result.success = len(result.code_blocks) > 0 or len(result.errors) == 0
            
        except Exception as e:
            result.errors.append(str(e))
        
        return result
    
    def _index_code(self, code_block: CodeBlock):
        """Index a code block for search"""
        # Create a unique key
        key = f"{code_block.source}:{code_block.file_path}:{code_block.line_start}"
        self._index[key] = code_block
        
        # Also index by language
        lang_key = f"lang:{code_block.language}"
        if lang_key not in self._index:
            self._index[lang_key] = code_block
    
    def search(self, query: str, 
               language: Optional[str] = None,
               source: Optional[str] = None) -> List[CodeBlock]:
        """Search indexed code blocks"""
        results = []
        query_lower = query.lower()
        
        for key, block in self._index.items():
            # Filter by language if specified
            if language and block.language != language:
                continue
            
            # Filter by source if specified
            if source and block.source != source:
                continue
            
            # Search in code content
            if query_lower in block.code.lower():
                results.append(block)
            # Search in metadata
            elif any(query_lower in str(v).lower() 
                    for v in block.metadata.values()):
                results.append(block)
        
        return results
    
    def get_indexed_blocks(self) -> List[CodeBlock]:
        """Get all indexed code blocks"""
        return list(self._index.values())
    
    def clear_index(self):
        """Clear the code index"""
        self._index.clear()
        self._harvested_files.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get harvesting statistics"""
        return {
            "total_blocks": len(self._index),
            "total_files": len(self._harvested_files),
            "languages": self._get_language_stats(),
            "sources": self._get_source_stats()
        }
    
    def _get_language_stats(self) -> Dict[str, int]:
        """Get statistics by language"""
        stats = {}
        for block in self._index.values():
            lang = block.language
            stats[lang] = stats.get(lang, 0) + 1
        return stats
    
    def _get_source_stats(self) -> Dict[str, int]:
        """Get statistics by source"""
        stats = {}
        for block in self._index.values():
            source = block.source
            stats[source] = stats.get(source, 0) + 1
        return stats


# Global harvester instance
_harvester: Optional[CodeHarvester] = None


def get_harvester() -> CodeHarvester:
    """Get or create the global CodeHarvester instance"""
    global _harvester
    if _harvester is None:
        _harvester = CodeHarvester()
    return _harvester


def reset_harvester():
    """Reset the global harvester instance"""
    global _harvester
    _harvester = None


if __name__ == "__main__":
    # Example usage
    harvester = get_harvester()
    
    # Harvest from text
    test_text = """
Here's some Python code:

```python
def hello():
    print("Hello, World!")
```

And some JavaScript:

```javascript
function test() {
    console.log("test");
}
```
"""
    
    result = harvester.harvest_from_text(test_text, "test_source")
    print(f"Harvested {len(result.code_blocks)} code blocks")
    for block in result.code_blocks:
        print(f"  - {block.language}: {block.code[:50]}...")
    
    # Search
    search_results = harvester.search("print")
    print(f"Found {len(search_results)} blocks containing 'print'")
    
    # Statistics
    stats = harvester.get_statistics()
    print(f"Statistics: {stats}")
