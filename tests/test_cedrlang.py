import pytest
import tempfile
from pathlib import Path
from workspace.compression_sandbox.cedrlang.cedrlang import (
    compile_doc,
    decompile_doc,
    compress,
    expand,
    caveman
)

def test_1337speak_and_grimoire_translation():
    orig = "We need to transmute the code and scry the output, then cast a spell from the grimoire."
    expected = "We need to h4x the code and scry the output, then c4st a spell from the gr1m01r3."

    compiled = compile_doc(orig)
    assert compiled == expected

    decompiled = decompile_doc(compiled)
    assert decompiled == orig

def test_casing_preservation():
    assert compile_doc("Transmute") == "H4x"
    assert decompile_doc("H4x") == "Transmute"

    assert compile_doc("transmute") == "h4x"
    assert decompile_doc("h4x") == "transmute"

    assert compile_doc("TRANSMUTE") == "H4X"
    assert decompile_doc("H4X") == "TRANSMUTE"

def test_bullet_and_formatting_preservation():
    orig_bullets = (
        "- We need a scry of the codebase.\n"
        "* Please transmute this function.\n"
        "1. Cast the spell."
    )
    expected_bullets = (
        "- We need a scry of the codebase.\n"
        "* Please h4x this function.\n"
        "1. C4st the spell."
    )

    compiled = compile_doc(orig_bullets)
    assert compiled == expected_bullets
    assert decompile_doc(compiled) == orig_bullets

def test_fenced_code_protection():
    orig = (
        "Here is some human text to transmute.\n"
        "```python\n"
        "def transmute(code):\n"
        "    return scry(code)\n"
        "```\n"
        "And more transmute text."
    )
    expected = (
        "Here is some human text to h4x.\n"
        "```python\n"
        "def transmute(code):\n"
        "    return scry(code)\n"
        "```\n"
        "And more h4x text."
    )

    compiled = compile_doc(orig)
    assert compiled == expected
    assert decompile_doc(compiled) == orig

def test_html_and_inline_code_protection():
    orig = "Run `transmute` inside the <div>transmute</div> container."
    expected = "Run `transmute` inside the <div>h4x</div> container."

    compiled = compile_doc(orig)
    assert compiled == expected
    assert decompile_doc(compiled) == orig

def test_decimal_number_and_filename_protection():
    orig = "Check python script deepcli/deepcli/core.py for version 12.34."
    compiled = compile_doc(orig)
    assert compiled == orig
    assert decompile_doc(compiled) == orig

def test_markdown_bold_and_emphasis_protection():
    orig = "This is **transmute** and *scry* and __transmute__ and _scry_."
    expected = "This is **h4x** and *scry* and __h4x__ and _scry_."

    compiled = compile_doc(orig)
    assert compiled == expected
    assert decompile_doc(compiled) == orig

def test_punctuation_exclusion_and_boundaries():
    orig = "transmute, transmute. transmute! transmute? (transmute) [transmute]"
    expected = "h4x, h4x. h4x! h4x? (h4x) [h4x]"

    compiled = compile_doc(orig)
    assert compiled == expected
    assert decompile_doc(compiled) == orig

def test_link_protection_and_translation():
    orig = "Please click [transmute](http://scry.com/transmute) to transmute."
    expected = "Please click [h4x](http://scry.com/transmute) to h4x."

    compiled = compile_doc(orig)
    assert compiled == expected
    assert decompile_doc(compiled) == orig

def test_emerging_technologies_procurement_mappings():
    orig = "We are researching emerging technology curation and procurement compliance."
    expected = "We are researching em_t3ch cur473 and pr0cur3 c0mp1."
    compiled = compile_doc(orig)
    assert compiled == expected

    decompiled = decompile_doc(compiled)
    assert decompiled == orig

def test_caveman_six_lines():
    res1 = caveman("success leads to update")
    assert res1 == "✓ → ~"

    res2 = caveman("success leads to update", max_up=True)
    assert res2 == "✓ → ~"

    res4 = caveman("the quick brown fox", max_up=True)
    assert res4 == "QUICK BROWN FOX"
