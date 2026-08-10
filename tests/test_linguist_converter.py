import os
import pytest
from workspace.compression_sandbox.cedrlang.cedrlang import compress, expand, caveman

def test_caveman_stripper():
    text = "the quick brown fox is jumping and then he was gone"
    res = caveman(text)
    words = res.lower().split()
    assert "the" not in words
    assert "was" not in words
    assert "is" not in words
    assert "quick" in words

def test_symbol_substitutions():
    text = "the process leads to success because of rules"
    compressed = compress(text, aggressive=False)
    assert "→" in compressed
    assert "←" in compressed

def test_grimoire_mappings():
    text = "the manager agent will review the task queue"
    compressed = compress(text, aggressive=False)
    assert "4rchW1z4rd" in compressed
    assert "5cry" in compressed or "scry" in compressed or "5cry" in expand(compressed)

def test_markdown_preservation():
    text = "Please review this link [Google](https://google.com) and code `import sys` or ```def my_func(): pass```"
    compressed = compress(text)
    assert "[Google](https://google.com)" in compressed
    assert "`import sys`" in compressed
    assert "```def my_func(): pass```" in compressed

def test_expansion_reversal():
    text = "the manager agent will update the task queue"
    compressed = compress(text)
    expanded = expand(compressed)
    assert "manager agent" in expanded.lower()
    assert "~" in expanded
    assert "task queue" in expanded.lower()

def test_indentation_preservation():
    # Test nested lists and indented text preserve leading whitespaces
    text = "- Both gates:\n  - python3 scripts/ci/repo_gate.py\n  - deeper nested text"
    compressed = compress(text, aggressive=False)
    lines = compressed.split('\n')
    assert lines[0].startswith("-")
    assert lines[1].startswith("  -")
    assert lines[2].startswith("  -")

def test_url_and_path_protection():
    # Test bare URLs and file paths are not substituted
    text = "see https://example.com/review/agent/test.html for details about scripts/ci/repo_gate.py"
    compressed = compress(text, aggressive=False)
    assert "https://example.com/review/agent/test.html" in compressed
    assert "scripts/ci/repo_gate.py" in compressed

def test_true_false_expansion():
    # Test T and F expand to true and false
    compressed = "T ∧ F"
    expanded = expand(compressed)
    assert "true" in expanded.lower()
    assert "false" in expanded.lower()

def test_no_spurious_punctuation_expansion():
    # Test standard punctuation is not expanded
    text = "This is a sentence. It has a hyphen-ated word!"
    expanded = expand(text)
    # Reversing standard punctuation like '.' or '!' should not turn into words
    assert "This is a sentence." in expanded
    assert "word!" in expanded

def test_trailing_newline_preservation():
    # Test trailing newline is preserved
    text = "line one\nline two\n"
    compressed = compress(text)
    assert compressed.endswith('\n')
    expanded = expand(compressed)
    assert expanded.endswith('\n')
