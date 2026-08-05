#!/usr/bin/env python3
"""Tests for harvesters module."""
import pytest
import os
import tempfile
from pathlib import Path

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from harvesters.code_harvester import CodeHarvester, CodeBlock, CodexIndex, Pointer, TaxonomyNode
from harvesters.search_engine import SearchEngine, SearchResult
from harvesters.extractor import CodeExtractor, ExtractedCode
from harvesters.analyzer import CodeAnalyzer, AnalysisResult


class TestCodeHarvester:
    """Test code harvester functionality."""
    
    def test_harvest_file(self):
        """Test harvesting code from a file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def hello():\n    print('Hello, World!')\n")
            file_path = f.name
        
        try:
            harvester = CodeHarvester()
            code_blocks = harvester.harvest_file(file_path)
            
            assert len(code_blocks) == 1
            assert code_blocks[0].language == "python"
            assert "def hello():" in code_blocks[0].content
        finally:
            os.unlink(file_path)
    
    def test_harvest_directory(self):
        """Test harvesting code from a directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            py_file = Path(tmpdir) / "test.py"
            py_file.write_text("def test():\n    pass\n")
            
            js_file = Path(tmpdir) / "test.js"
            js_file.write_text("function test() {}\n")
            
            harvester = CodeHarvester()
            code_blocks = harvester.harvest_directory(tmpdir, recursive=False)
            
            assert len(code_blocks) == 2
            languages = {b.language for b in code_blocks}
            assert "python" in languages
            assert "javascript" in languages
    
    def test_harvest_from_text(self):
        """Test harvesting code from session messages."""
        text = """Here's some code:
        
        ```python
        def hello():
            print("Hello")
        ```
        
        And some JavaScript:
        
        ```javascript
        function test() {}
        ```
        """
        
        harvester = CodeHarvester()
        messages = [{"role": "assistant", "content": text}]
        code_blocks = harvester.harvest_from_session("test_session", messages, "Test")
        
        # We expect at least 2 code blocks (python and javascript)
        assert len(code_blocks) >= 2
        languages = {b.language for b in code_blocks}
        assert "python" in languages
        assert "javascript" in languages
    
    def test_code_block(self):
        """Test CodeBlock class."""
        code_block = CodeBlock(
            content="def test():\n    pass",
            language="python",
            session_id="test_session",
            message_index=0,
            block_index=0,
        )
        
        assert code_block.content_hash != ""
        assert len(code_block.content_hash) == 16
        assert code_block.language == "python"
        
        # Test serialization
        data = code_block.to_dict()
        assert "content" in data
        assert "language" in data
        assert "content_hash" in data
        
        # Test deserialization
        new_block = CodeBlock.from_dict(data)
        assert new_block.content == code_block.content
        assert new_block.content_hash == code_block.content_hash
    
    def test_codex_index(self):
        """Test CodexIndex functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            codex = CodexIndex(Path(tmpdir))
            
            messages = [
                {"role": "user", "content": "Write a function"},
                {"role": "assistant", "content": "```python\ndef hello():\n    print('Hello')\n```"}
            ]
            
            codex.index_conversation("test_session", "Test", messages)
            
            # Check that we can search
            results = codex.search("hello")
            assert len(results) >= 1
            
            # Check that we can get by hash
            if results:
                code = codex.get_code_by_hash(results[0]['hash'])
                assert code is not None
                assert "def hello" in code


class TestSearchEngine:
    """Test search engine functionality."""
    
    def test_index_conversation(self):
        """Test indexing a conversation."""
        engine = SearchEngine()
        
        messages = [
            {"role": "user", "content": "Write a function"},
            {"role": "assistant", "content": "```python\ndef hello():\n    print('Hello')\n```"}
        ]
        
        engine.index_conversation("test_session", "Test", messages)
        
        # Check that we can search
        results = engine.search("hello")
        assert len(results) >= 1
    
    def test_search(self):
        """Test searching code blocks."""
        engine = SearchEngine()
        
        messages = [
            {"role": "assistant", "content": "```python\ndef add(a, b):\n    return a + b\n```"},
            {"role": "assistant", "content": "```python\ndef sub(a, b):\n    return a - b\n```"}
        ]
        
        engine.index_conversation("test_session", "Test", messages)
        
        # Search for "def"
        results = engine.search("def")
        assert len(results) >= 2
        
        # Search for "add"
        results = engine.search("add")
        assert len(results) >= 1
        assert "add" in results[0].content
    
    def test_search_by_language(self):
        """Test searching by language."""
        engine = SearchEngine()
        
        messages = [
            {"role": "assistant", "content": "```python\ndef test():\n    pass\n```"},
            {"role": "assistant", "content": "```javascript\nfunction test() {}\n```"}
        ]
        
        engine.index_conversation("test_session", "Test", messages)
        
        # Search for Python
        results = engine.search_by_language("python")
        assert len(results) >= 1
        assert results[0].language == "python"
        
        # Search for JavaScript
        results = engine.search_by_language("javascript")
        assert len(results) >= 1
        assert results[0].language == "javascript"


class TestCodeExtractor:
    """Test code extractor functionality."""
    
    def test_extract_from_text(self):
        """Test extracting code from text."""
        text = """
        Here's some Python:
        
        ```python
        def hello():
            print("Hello")
        ```
        """
        
        extractor = CodeExtractor()
        extracted = extractor.extract_from_text(text, "test")
        
        assert len(extracted) == 1
        assert extracted[0].language == "python"
        assert "def hello():" in extracted[0].content
    
    def test_extract_markdown_code(self):
        """Test extracting markdown code blocks."""
        markdown = """
        # Code Example
        
        ```python
        def test():\n            pass
        ```
        
        ```javascript
        function test() {}
        ```
        """
        
        extractor = CodeExtractor()
        extracted = extractor.extract_from_text(markdown, "test")
        
        assert len(extracted) == 2
        languages = {e.language for e in extracted}
        assert "python" in languages
        assert "javascript" in languages
    
    def test_detect_language(self):
        """Test language detection."""
        extractor = CodeExtractor()
        
        # Test by extension
        assert extractor._detect_language("test.py") == "python"
        assert extractor._detect_language("test.js") == "javascript"
        assert extractor._detect_language("test.html") == "html"
        
        # Test by content
        assert extractor._detect_language_from_content("def test():\n    pass") == "python"
        assert extractor._detect_language_from_content("function test() {}") == "javascript"


class TestCodeAnalyzer:
    """Test code analyzer functionality."""
    
    def test_analyze_python(self):
        """Test analyzing Python code."""
        code = """
def hello(name):
    '''Say hello'''
    print(f"Hello, {name}!")

def add(a, b):
    return a + b

class Calculator:
    def multiply(self, x, y):
        return x * y
"""
        
        analyzer = CodeAnalyzer()
        result = analyzer.analyze(code, "python")
        
        # We expect at least 2 functions (hello, add, and multiply method)
        assert len(result.functions) >= 2
        assert len(result.classes) == 1
        assert result.metadata["language"] == "python"
        
        # Check function names
        func_names = {f["name"] for f in result.functions}
        assert "hello" in func_names
        assert "add" in func_names
        
        # Check class name
        class_names = {c["name"] for c in result.classes}
        assert "Calculator" in class_names
    
    def test_analyze_javascript(self):
        """Test analyzing JavaScript code."""
        code = """
function hello(name) {
    console.log(`Hello, ${name}!`);
}

function add(a, b) {
    return a + b;
}

class Calculator {
    multiply(x, y) {
        return x * y;
    }
}
"""
        
        analyzer = CodeAnalyzer()
        result = analyzer.analyze(code, "javascript")
        
        assert len(result.functions) >= 2
        assert len(result.classes) >= 1
        assert result.metadata["language"] == "javascript"
    
    def test_analyze_generic(self):
        """Test generic code analysis."""
        code = "This is just some text with no specific language features."
        
        analyzer = CodeAnalyzer()
        result = analyzer.analyze(code, "text")
        
        assert result.metadata["language"] == "text"
        assert result.metadata["line_count"] == 1
        assert result.metadata["char_count"] == len(code)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
