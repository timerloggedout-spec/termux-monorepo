import random

from workspace.compression_sandbox.cedrlang.phase_codec import (
    INITIAL_SUBSTITUTION_PROBABILITY,
    from_1337speak,
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


from workspace.compression_sandbox.cedrlang.phase_codec import ConversationalSteganographyCipher


def test_conversational_steganography_encode_decode_roundtrip():
    payload = "Agent2Agent confidential command: +h4x ~pr0b3 !scry"
    stego = ConversationalSteganographyCipher.encode(payload)
    assert ConversationalSteganographyCipher.has_stego(stego)
    recovered = ConversationalSteganographyCipher.decode(stego)
    assert recovered == payload


def test_conversational_steganography_with_host_text():
    payload = "Secret CedrLang payload"
    host = "Hello world, this is a normal conversational message."
    stego_text = ConversationalSteganographyCipher.encode(payload, host_text=host)
    assert ConversationalSteganographyCipher.has_stego(stego_text)
    # The host text should still be readable in plain text
    assert "Hello" in stego_text and "world" in stego_text
    recovered = ConversationalSteganographyCipher.decode(stego_text)
    assert recovered == payload


def test_conversational_steganography_with_secret_key():
    payload = "Encrypted private mapping payload"
    key = "gr1m01r3_53cr37_k3y"
    stego_text = ConversationalSteganographyCipher.encode(payload, host_text="Public text", secret_key=key)
    assert ConversationalSteganographyCipher.has_stego(stego_text)

    # Decoding without key or with wrong key fails to produce original payload
    assert ConversationalSteganographyCipher.decode(stego_text, secret_key="wrong_key") != payload
    # Decoding with correct key succeeds losslessly
    assert ConversationalSteganographyCipher.decode(stego_text, secret_key=key) == payload


def test_conversational_steganography_has_stego_fastpath():
    assert not ConversationalSteganographyCipher.has_stego("Plain text without zero-width chars")
    assert not ConversationalSteganographyCipher.has_stego("")
    assert ConversationalSteganographyCipher.decode("Plain text without stego") == ""
