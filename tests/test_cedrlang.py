import pytest
import sys
import os

# Ensure the correct path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'workspace', 'compression_sandbox', 'cedrlang')))

from cedrlang import (
    compile_document,
    decompile_document,
    compile_line,
    decompile_line,
    protect_line,
    restore_line
)

def test_1337speak_conversion():
    text = "We have elite hacks and extreme skills."
    compiled = compile_document(text)
    assert "1337" in compiled
    assert "h4x" in compiled
    assert "sk1llz" in compiled

    # Test round trip
    assert decompile_document(compiled).lower() == text.lower()


def test_grimoire_mappings():
    text = "The Agent should test the code and refactor it."
    compiled = compile_document(text)
    assert "C4573r" in compiled
    assert "Pr0b3" in compiled or "pr0b3" in compiled
    assert "Tr4n5mu73" in compiled or "tr4n5mu73" in compiled

    # Round trip
    decompiled = decompile_document(compiled)
    assert "Agent" in decompiled
    assert "test" in decompiled.lower()
    assert "refactor" in decompiled.lower()


def test_formatting_bullet_preservation():
    text = """
1. First item: Agent success.
2. Second item: Refactor warning.
- Bullet point: Test fail.
* Another bullet: review pending.
### Header 3
    """
    compiled = compile_document(text)
    assert "1. " in compiled
    assert "2. " in compiled
    assert "- " in compiled
    assert "* " in compiled
    assert "### Header 3" in compiled

    decompiled = decompile_document(compiled)
    assert "1. " in decompiled
    assert "2. " in decompiled
    assert "- " in decompiled
    assert "* " in decompiled
    assert "### Header 3" in decompiled
    assert "Agent" in decompiled
    assert "review" in decompiled or "Review" in decompiled


def test_decimal_filename_number_protection():
    text = "Check the chmod 0o600 file AGENTS.md with value 3.14."
    compiled = compile_document(text)
    assert "0o600" in compiled
    assert "AGENTS.md" in compiled
    assert "3.14" in compiled

    decompiled = decompile_document(compiled)
    assert "0o600" in decompiled
    assert "AGENTS.md" in decompiled
    assert "3.14" in decompiled


def test_markdown_bold_emphasis_protection():
    text = "We have **unmodified bold** and *unmodified italics* here."
    compiled = compile_document(text)
    assert "**unmodified bold**" in compiled
    assert "*unmodified italics*" in compiled

    decompiled = decompile_document(compiled)
    assert "**unmodified bold**" in decompiled
    assert "*unmodified italics*" in decompiled


def test_code_blocks_and_links_protection():
    text = """
See [the link](https://example.com/AGENTS.md) or execute `chmod 0o700`.
```python
# Fenced code block: Agent must test code
def test():
    pass
```
"""
    compiled = compile_document(text)
    assert "[the link](https://example.com/AGENTS.md)" in compiled
    assert "`chmod 0o700`" in compiled
    assert "def test():" in compiled
    assert "Agent must test code" in compiled

    decompiled = decompile_document(compiled)
    assert "[the link](https://example.com/AGENTS.md)" in decompiled
    assert "`chmod 0o700`" in decompiled
    assert "def test():" in decompiled
    assert "Agent must test code" in decompiled


def test_round_trip_stability():
    doc = """# AGENTS.md — Termux monorepo

Instructions for coding agents (Grok, Claude, Codex, Devin, ChatGPT, local runners).

## Read first (in order)

1. **This file** (`AGENTS.md`)
2. [`docs/proposals/registry.yaml`](docs/proposals/registry.yaml) — what is active
3. [`docs/proposals/PROCESS.md`](docs/proposals/PROCESS.md) — post / debate / consensus / close
4. [`docs/PR-SUMMARY-PROCESS.md`](docs/PR-SUMMARY-PROCESS.md) — who may rewrite PR bodies (multi-agent)
5. [`docs/ARCHW1Z-GATE.md`](docs/ARCHW1Z-GATE.md) — repo-gate + termux-smoke

## Hard rules

- Target **`master-staging`**, not raw `master`, for integration work.
- Both gates must pass before merge:
  - `python3 scripts/ci/repo_gate.py`
  - `python3 scripts/ci/termux_smoke.py`
- Do not invent work outside `docs/proposals/active/<id>/ITEMS.md` — add a row first.
- Cite `Implements: <ITEM-ID>` on PRs/commits.
- **No** wholesale merge of PR #6 (TER-9) or PR #2 (Rust CI) — see disposition comments.
- **No** Class 3/4 artifacts in git (session stores, browser profiles, tokens).
- Unposted chat is not consensus — write Review log or DEBATE.md.
- PR body rewrites: follow `docs/PR-SUMMARY-PROCESS.md` roster (not a single-agent monopoly).
"""
    compiled = compile_document(doc)
    decompiled = decompile_document(compiled)

    assert "AGENTS.md" in decompiled
    assert "registry.yaml" in decompiled
    assert "PROCESS.md" in decompiled
    assert "master-staging" in decompiled
    assert "repo_gate.py" in decompiled
    assert "termux_smoke.py" in decompiled
    assert "Class 3/4" in decompiled
