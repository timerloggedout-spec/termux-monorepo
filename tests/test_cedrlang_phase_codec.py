import random

import pytest
from workspace.compression_sandbox.cedrlang.phase_codec import (
    INITIAL_SUBSTITUTION_PROBABILITY,
    ConversationalSteganographyCipher,
    from_1337speak,
    steganography_decode,
    steganography_encode,
    to_1337speak,
)


def test_initial_phase_is_historical_70_percent():
    assert INITIAL_SUBSTITUTION_PROBABILITY == 0.70


def test_zero_probability_is_identity():
    source = "h4x pr0b3 gr1m01r3"
    assert to_1337speak(source, probability=0.0) == source


def test_full_probability_is_reversible():
    source = "h4x pr0b3 gr1m01r3 l1ngu15t r3534rch c0nc3p7"
    encoded = to_1337speak(source, probability=1.0, rng=random.Random(7))
    assert encoded != source
    assert from_1337speak(encoded) == source


def test_initial_phase_is_seed_reproducible_and_round_trips():
    source = "h4x pr0b3 gr1m01r3 l1ngu15t"
    encoded_a = to_1337speak(source, rng=random.Random(42))
    encoded_b = to_1337speak(source, rng=random.Random(42))
    assert encoded_a == encoded_b
    assert from_1337speak(encoded_a) == source


def test_unknown_prose_and_numbers_are_untouched():
    source = "plain prose 123.45 /tmp/file.py h4x"
    encoded = to_1337speak(source, probability=1.0, rng=random.Random(1))
    assert "plain prose 123.45 /tmp/file.py" in encoded
    assert from_1337speak(encoded) == source


def test_probability_validation():
    for value in (-0.01, 1.01):
        try:
            to_1337speak("h4x", probability=value)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid probability was accepted")


def test_conversational_steganography_roundtrip():
    secret = "Top secret agent prompt: execute pre-parser transmute h4x"
    key = "Agent007-PrivateKey-2026"
    cover = "System telemetry status nominal."

    encoded = steganography_encode(secret, key, cover_text=cover)
    assert cover in encoded
    # The secret itself is hidden using invisible zero-width characters in cover
    assert secret not in encoded

    decoded = steganography_decode(encoded, key)
    assert decoded == secret


def test_conversational_steganography_invalid_key_and_payload():
    secret = "Confidential data"
    key_valid = "CorrectKey123"
    key_invalid = "WrongKey456"

    encoded = steganography_encode(secret, key_valid)

    with pytest.raises(ValueError, match="key cannot be empty"):
        ConversationalSteganographyCipher("")

    # Mismatched decryption key raises ValueError
    with pytest.raises(ValueError):
        steganography_decode(encoded, key_invalid)

    # Corrupted stego payload raises ValueError
    with pytest.raises(ValueError):
        steganography_decode("Invalid\u200b\u200cPayload", key_valid)
