import os
import pytest
from workspace.compression_sandbox.cedrlang.cedrlang import compress, expand, caveman

def test_caveman_stripper():
    # Test our exact 6-line caveman stripper
    text = "the quick brown fox is jumping and then he was gone"
    res = caveman(text)
    words = res.lower().split()
    assert "the" not in words
    assert "was" not in words
    assert "is" not in words
    assert "quick" in words

def test_symbol_substitutions():
    # Test causality symbol replacement
    text = "the process leads to success because of rules"
    compressed = compress(text, aggressive=False)
    assert "→" in compressed
    assert "←" in compressed

def test_grimoire_mappings():
    # Test grimoire translations (e.g., manager agent -> 4rchW1z4rd)
    text = "the manager agent will review the task queue"
    compressed = compress(text, aggressive=False)
    assert "4rchW1z4rd" in compressed
    assert "5cry" in compressed or "scry" in compressed or "5cry" in expand(compressed)

def test_markdown_preservation():
    # Test that code blocks and links are perfectly preserved
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
    assert "update" in expanded.lower()
    assert "task queue" in expanded.lower()
