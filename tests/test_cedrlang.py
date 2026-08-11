import tempfile
from pathlib import Path
from workspace.compression_sandbox.cedrlang import cedrlang

def test_symbol_substitution():
    text = "if true then success else error"
    compressed = cedrlang.compress(text, aggressive=False)
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
    assert "`x = 42`" in compressed
    assert "[this link](http://example.com)" in compressed

    expanded = cedrlang.expand(compressed)
    assert "`x = 42`" in expanded
    assert "[this link](http://example.com)" in expanded

def test_bold_emphasis_protection():
    text = "This is **bold** text and *italic* text."
    compressed = cedrlang.compress(text, aggressive=True)
    assert "**bold**" in compressed
    assert "*italic*" in compressed

    expanded = cedrlang.expand(compressed)
    assert "**bold**" in expanded
    assert "*italic*" in expanded

def test_line_preservation():
    text = "Line 1.\nLine 2.\nLine 3."
    compressed = cedrlang.compress(text, aggressive=True)
    assert "\n" in compressed
    assert len(compressed.splitlines()) == 3

    expanded = cedrlang.expand(compressed)
    assert "\n" in expanded
    assert len(expanded.splitlines()) == 3

def test_filename_and_number_protection():
    text = "The file registry.yaml has version v1.2 and config 42."
    compressed = cedrlang.compress(text, aggressive=True)
    # registry.yaml and v1.2 should not be mangled
    assert "registry.yaml" in compressed
    assert "v1.2" in compressed
    assert "42" in compressed

    expanded = cedrlang.expand(compressed)
    assert "registry.yaml" in expanded
    assert "v1.2" in expanded
    assert "42" in expanded

def test_caveman_stripper():
    text = "The quick brown fox is jumping over a lazy dog"
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
