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
    source = "h4x pr0b3 gr1m01r3 l1ngu15t"
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
