import os
import tempfile
from pathlib import Path
from workspace.compression_sandbox.cedrlang import cedrlang

def test_symbol_substitution():
    text = "if true then success else error"
    compressed = cedrlang.compress(text, aggressive=False)
    # expect symbols for if (?, then =>, success ✓, else |, error ⚠)
    assert "?" in compressed
    assert "⇒" in compressed
    assert "✓" in compressed
    assert "|" in compressed
    assert "⚠" in compressed

    expanded = cedrlang.expand(compressed)
    assert "if" in expanded
    assert "then" in expanded
    assert "success" in expanded
    assert "else" in expanded

def test_grimoire_mapping():
    text = "The ArchWizard uses a Caster to increase Mana"
    compressed = cedrlang.compress(text, aggressive=False)
    assert "4rchW1z4rd" in compressed
    assert "C4573r" in compressed
    assert "M4n4" in compressed

    expanded = cedrlang.expand(compressed)
    assert "ArchWizard" in expanded
    assert "Caster" in expanded

def test_placeholder_protection():
    text = "Please review the code in `x = 42` and check [this link](http://example.com) for details."
    compressed = cedrlang.compress(text, aggressive=True)
    # The protected parts must remain exactly untouched
    assert "`x = 42`" in compressed
    assert "[this link](http://example.com)" in compressed

    expanded = cedrlang.expand(compressed)
    assert "`x = 42`" in expanded
    assert "[this link](http://example.com)" in expanded

def test_caveman_stripper():
    text = "The quick brown fox is jumping over a lazy dog"
    # 'The', 'is', 'a' are stopwords and should be removed
    stripped = cedrlang.caveman_strip(text)
    words = stripped.split()
    assert "The" not in words
    assert "the" not in words
    assert "is" not in words
    assert "a" not in words
    assert "quick" in words
    assert "lazy" in words

def test_compile_decompile_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        input_file = Path(tmpdir) / "input.md"
        output_file = Path(tmpdir) / "output.md"
        decomp_file = Path(tmpdir) / "decomp.md"

        content = "The ArchWizard is acting because of a warning.\nCheck `sys.exit()`."
        input_file.write_text(content, encoding="utf-8")

        # Compile
        compiled_text = cedrlang.compress(content, aggressive=True)
        output_file.write_text(compiled_text, encoding="utf-8")

        assert "4rchW1z4rd" in compiled_text
        assert "`sys.exit()`" in compiled_text

        # Decompile
        decompiled_text = cedrlang.expand(compiled_text)
        decomp_file.write_text(decompiled_text, encoding="utf-8")

        assert "ArchWizard" in decompiled_text
        assert "`sys.exit()`" in decompiled_text
