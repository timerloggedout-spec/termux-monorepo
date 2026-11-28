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


def test_conversational_steganography_cipher_roundtrip():
    from workspace.compression_sandbox.cedrlang.phase_codec import ConversationalSteganographyCipher

    payload = "Agent-2-Agent secret instruction: execute build!"
    cover = "Everything is running smoothly."
    key = "private_secret_key"

    encoded = ConversationalSteganographyCipher.encode(payload, cover_text=cover, key=key)
    assert ConversationalSteganographyCipher.has_payload(encoded) is True

    decoded_payload, clean_cover = ConversationalSteganographyCipher.decode(encoded, key=key)
    assert decoded_payload == payload
    assert clean_cover == cover


def test_conversational_steganography_key_isolation():
    from workspace.compression_sandbox.cedrlang.phase_codec import ConversationalSteganographyCipher

    payload = "Top secret data"
    encoded = ConversationalSteganographyCipher.encode(payload, key="key_A")

    # Decoding with incorrect key yields garbage/mismatched string
    wrong_decoded, _ = ConversationalSteganographyCipher.decode(encoded, key="key_B")
    assert wrong_decoded != payload


def test_conversational_steganography_plain_text_has_no_payload():
    from workspace.compression_sandbox.cedrlang.phase_codec import ConversationalSteganographyCipher

    plain_text = "Standard plain text message without hidden stego quads."
    assert ConversationalSteganographyCipher.has_payload(plain_text) is False
    decoded_payload, clean_text = ConversationalSteganographyCipher.decode(plain_text)
    assert decoded_payload == ""
    assert clean_text == plain_text
