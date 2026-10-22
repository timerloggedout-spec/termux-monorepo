import random

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


def test_conversational_steganography_cipher_roundtrip():
    cipher = ConversationalSteganographyCipher(key="secret_grimoire_key_123")
    text = "h4x pr0b3 gr1m01r3 l1ngu15t"
    encoded = cipher.steganography_encode(text)
    assert encoded != text
    decoded = cipher.steganography_decode(encoded)
    assert decoded == text


def test_conversational_steganography_functional_interface():
    text = "h4x pr0b3 gr1m01r3"
    key = "agent2agent_lane4"
    encoded = steganography_encode(text, key=key)
    assert encoded != text
    decoded = steganography_decode(encoded, key=key)
    assert decoded == text


def test_conversational_steganography_different_keys_produce_different_ciphers():
    text = "h4x pr0b3 gr1m01r3"
    encoded_a = steganography_encode(text, key="key_alpha")
    encoded_b = steganography_encode(text, key="key_beta")
    assert encoded_a != encoded_b
