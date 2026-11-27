"""Exact-ratio rhythmic composition and polyphonic overlay primitives."""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from functools import reduce
from math import gcd, lcm
from typing import Iterable

def exact_ratio(numerator: int, denominator: int = 1) -> Fraction:
    """Return a reduced exact rational ratio."""
    if denominator == 0:
        raise ValueError("ratio denominator must be non-zero")
    return Fraction(numerator, denominator)

def rational_lcm(values: Iterable[Fraction]) -> Fraction:
    """Return the least positive rational multiple shared by every value."""
    items = [Fraction(value) for value in values]
    if not items or any(value <= 0 for value in items):
        raise ValueError("rational_lcm requires positive values")
    numerator = reduce(lcm, (value.numerator for value in items))
    denominator = reduce(gcd, (value.denominator for value in items))
    return Fraction(numerator, denominator)

def common_subdivision(values: Iterable[Fraction]) -> int:
    """Return the smallest integer grid that represents every ratio exactly."""
    items = [Fraction(value) for value in values]
    if not items:
        raise ValueError("common_subdivision requires at least one ratio")
    return reduce(lcm, (value.denominator for value in items))

@dataclass(frozen=True)
class RhythmicLayer:
    voice: str
    period: Fraction
    offsets: tuple[Fraction, ...]
    phase: Fraction = Fraction(0)
    def __post_init__(self) -> None:
        if not self.voice.strip():
            raise ValueError("voice is required")
        if self.period <= 0:
            raise ValueError("period must be positive")
        if not (0 <= self.phase < self.period):
            raise ValueError("phase must be in [0, period)")
        if not self.offsets:
            raise ValueError("at least one onset offset is required")
        if any(offset < 0 or offset >= self.period for offset in self.offsets):
            raise ValueError("onset offsets must fall inside the layer period")

@dataclass(frozen=True, order=True)
class RhythmicOnset:
    at: Fraction
    voice: str

@dataclass(frozen=True)
class Overlay:
    supercycle: Fraction
    subdivision: int
    onsets: tuple[RhythmicOnset, ...]
    coincidences: tuple[tuple[Fraction, tuple[str, ...]], ...]

def overlay_layers(layers: Iterable[RhythmicLayer]) -> Overlay:
    """Expand polyphonic layers over their exact shared supercycle."""
    collection = tuple(layers)
    if not collection:
        raise ValueError("overlay requires at least one rhythmic layer")
    cycle = rational_lcm(layer.period for layer in collection)
    grid = common_subdivision([
        cycle, *(layer.period for layer in collection),
        *(layer.phase for layer in collection),
        *(offset for layer in collection for offset in layer.offsets)
    ])
    events: list[RhythmicOnset] = []
    for layer in collection:
        repeat_count = int(cycle / layer.period)
        for repeat_index in range(repeat_count):
            base = layer.phase + repeat_index * layer.period
            for offset in layer.offsets:
                onset = (base + offset) % cycle
                events.append(RhythmicOnset(onset, layer.voice))
    events.sort()
    voices_by_time: dict[Fraction, set[str]] = {}
    for event in events:
        voices_by_time.setdefault(event.at, set()).add(event.voice)
    collisions = tuple(
        (at, tuple(sorted(voices)))
        for at, voices in sorted(voices_by_time.items())
        if len(voices) > 1
    )
    return Overlay(cycle, grid, tuple(events), collisions)
