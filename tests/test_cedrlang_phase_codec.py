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


def test_conversational_steganography_roundtrip():
    secret_directive = "Execute deployment phase 4 on production cluster."
    stegotext = steganography_encode(secret_directive)
    assert stegotext != secret_directive
    # Cover text remains visible around zero-width embedded secret payload
    assert stegotext.startswith("Greetings")
    assert "Execution proceeds nominally." in stegotext
    recovered = steganography_decode(stegotext)
    assert recovered == secret_directive


def test_conversational_steganography_with_private_mapping():
    private_key = {"production": "PRD_N0D3", "deployment": "D3PL0Y_M4N1F357"}
    secret = "deployment on production"
    cipher = ConversationalSteganographyCipher(private_key)
    stegotext = cipher.encode(secret)
    recovered = cipher.decode(stegotext)
    assert recovered == secret


def test_conversational_steganography_empty_and_cover_text():
    assert steganography_decode("") == ""
    assert steganography_encode("") == "Greetings agent. Execution proceeds nominally."
