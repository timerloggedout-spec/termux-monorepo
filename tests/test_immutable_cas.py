import os
import tempfile
from pathlib import Path
import pytest
import importlib

synthegration_index = importlib.import_module("cli-synthegration.synthegration_index")
Pointer = synthegration_index.Pointer
CodexIndex = synthegration_index.CodexIndex

def test_pointer_legacy_and_new_initialization():
    # Test new structure
    p = Pointer(
        provider="anthropic",
        account="dev-01",
        session="sess-abc",
        message=5,
        block=2,
        content_hash="f63e5e2b8f0e"
    )
    assert p.provider == "anthropic"
    assert p.account == "dev-01"
    assert p.session == "sess-abc"
    assert p.session_id == "sess-abc"
    assert p.message == 5
    assert p.message_index == 5
    assert p.block == 2
    assert p.block_index == 2
    assert p.content_hash == "f63e5e2b8f0e"
    assert p.to_key() == "anthropic:dev-01:sess-abc:5:2"

    # Test legacy structure (positional)
    p_legacy = Pointer("legacy-session", 10, 4, "abcdef123456")
    assert p_legacy.provider == "unknown"
    assert p_legacy.account == "unknown"
    assert p_legacy.session == "legacy-session"
    assert p_legacy.session_id == "legacy-session"
    assert p_legacy.message == 10
    assert p_legacy.message_index == 10
    assert p_legacy.block == 4
    assert p_legacy.block_index == 4
    assert p_legacy.content_hash == "abcdef123456"

def test_pointer_wire_serialization():
    p = Pointer(
        provider="openai",
        account="acct-99",
        session="sess-xyz",
        message=1,
        block=3,
        content_hash="aa11bb22cc33"
    )
    wire = p.to_wire()
    p_decoded = Pointer.from_wire(wire)

    assert p_decoded.provider == "openai"
    assert p_decoded.account == "acct-99"
    assert p_decoded.session == "sess-xyz"
    assert p_decoded.message == 1
    assert p_decoded.block == 3
    assert p_decoded.content_hash == "aa11bb22cc330000" # Zero padded/aligned

def test_immutable_cas_directory_writes():
    with tempfile.TemporaryDirectory() as tmp_dir:
        base_path = Path(tmp_dir)
        idx = CodexIndex(base_path)

        # Ingest a conversation to trigger indexing and CAS write
        messages = [
            {"role": "user", "content": "Write a test\n```python\nprint('hello')\n```", "inserted_at": "2026-08-01T12:00:00+00:00"}
        ]
        idx.index_conversation("session-test-01", "My Test Project", messages)

        # Verify that blob is written under the correct immutable CAS hierarchical structure:
        # blob/sha256/ch[:2]/ch
        code = "print('hello')\n"
        import hashlib
        ch = hashlib.sha256(code.encode()).hexdigest()

        expected_path = base_path / 'blob' / 'sha256' / ch[:2] / ch
        assert expected_path.exists()
        assert expected_path.read_text() == code
