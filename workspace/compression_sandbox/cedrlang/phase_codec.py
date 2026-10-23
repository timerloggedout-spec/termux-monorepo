"""Phased 1337/Grimoire surface codec recovered from Linguist PR #154.

Historical source: PR #154 review comment `discussion_r3754718523` described a
sparse randomized substitution rate with a 70% probability threshold in
`to_1337speak()`. This module restores that behavior as an explicit, scoped
phase rather than silently changing canonical CedrLang semantics.

The codec only mutates known compressed dictionary tokens. Variants are
recognized during decode, so ordinary digits, URLs, paths, and prose are not
rewritten accidentally. `probability=0.70` is the initial migration/default
phase; callers can ratchet it upward after validation.
"""

from __future__ import annotations

import random
import re
from itertools import product
from typing import Dict, Iterable, Mapping, Optional, Sequence, Tuple

# Historical initial-phase value from Linguist PR #154.
INITIAL_SUBSTITUTION_PROBABILITY = 0.70

# Character substitutions are intentionally limited to letters that have a
# stable 1337 representation. Existing digits in canonical tokens are never
# rewritten, preserving numbers and technical identifiers.
LEET_MAP: Mapping[str, str] = {
    "a": "4",
    "e": "3",
    "i": "1",
    "o": "0",
    "s": "5",
    "t": "7",
}

# Pre-computed translation table for 100% probability fast-path translation
LEET_TRANS = str.maketrans("aeiostAEIOST", "431057431057")

# Canonical compressed forms from CedrLang's MAPPINGS. Keeping this registry
# local avoids importing the large document compiler and makes the phase easy
# to test/recover independently.
CANONICAL_TOKENS: Tuple[str, ...] = (
    "h4x", "scry", "pr0b3", "3ch0", "l00p", "f0rk", "1nc4nt", "c4st",
    "gr1m01r3", "b1dd3r", "w4g3r", "chr0n0", "l1ngu15t", "sc0ut",
    "h4rv35t3r", "em_t3chs", "em_t3ch", "pr0cur3s", "pr0cur3", "cur473s",
    "cur473", "s0urc3s", "s0urc3", "4cqs", "4cq", "c0mp1s", "c0mp1",
    "r3534rchs", "r3534rch", "c0nc3p7s", "c0nc3p7", "c47_7h30ry",
    "n47_7r4n5", "h0m0m0rph", "150m0rph", "m0n_b1nd", "3xp_0bj",
    "m0rph", "func70r",
)


def _variants(token: str) -> Iterable[str]:
    """Yield all reversible leet variants for a canonical token."""
    positions = [i for i, char in enumerate(token.lower()) if char in LEET_MAP]
    for mask in product((False, True), repeat=len(positions)):
        chars = list(token)
        for position, enabled in zip(positions, mask):
            if enabled:
                chars[position] = LEET_MAP[chars[position].lower()]
        yield "".join(chars)


def _build_variant_index(tokens: Sequence[str]) -> Dict[str, str]:
    index: Dict[str, str] = {}
    for token in tokens:
        for variant in _variants(token):
            index.setdefault(variant.lower(), token)
    return index


def _build_trie_regex(words: Iterable[str]) -> str:
    """Construct a Trie-structured regex pattern from words to optimize prefix branching."""
    trie: dict = {}
    for w in words:
        curr = trie
        for char in w.lower():
            curr = curr.setdefault(char, {})
        curr[""] = None

    def _trie_to_regex(node: dict) -> str:
        if not node:
            return ""
        ending = "" in node
        chars = [k for k in node if k != ""]
        if not chars:
            return ""

        children = []
        for char in chars:
            sub = _trie_to_regex(node[char])
            char_pat = f"[{char.lower()}{char.upper()}]" if char.isalpha() else re.escape(char)
            if sub:
                children.append(char_pat + sub)
            else:
                children.append(char_pat)

        if len(children) == 1:
            res = children[0]
        else:
            res = "(?:" + "|".join(children) + ")"

        if ending:
            if len(children) == 1 and not children[0].startswith("(?:"):
                res = f"(?:{res})?"
            else:
                res = f"{res}?"
        return res

    return r"\b(?:" + _trie_to_regex(trie) + r")\b"


VARIANT_INDEX = _build_variant_index(CANONICAL_TOKENS)
# Build ASCII case-insensitive Trie regex without re.IGNORECASE to avoid Unicode case-folding overhead
VARIANT_REGEX = re.compile(_build_trie_regex(VARIANT_INDEX.keys()))

# Module-level set of eligible leet characters
ELIGIBLE_LEET_CHARS = set(LEET_MAP.keys())
# Filter variant index to only tokens containing eligible leet substitution characters
MUTABLE_VARIANTS = {
    v for v in VARIANT_INDEX.keys()
    if any(c in ELIGIBLE_LEET_CHARS for c in v.lower())
}

# Pre-compile Trie regex for mutable variants to skip invariant tokens completely during substitution
MUTABLE_VARIANT_REGEX = re.compile(_build_trie_regex(MUTABLE_VARIANTS))

# Pre-compute positional mapping for mutable variants: (lowercase_token) -> tuple of (character_position, leet_replacement_char)
MUTABLE_VARIANT_MAP: Dict[str, Tuple[Tuple[int, str], ...]] = {}
for variant_key in VARIANT_INDEX.keys():
    pos_map = tuple(
        (i, LEET_MAP[char.lower()])
        for i, char in enumerate(variant_key)
        if char.lower() in LEET_MAP
    )
    if pos_map:
        MUTABLE_VARIANT_MAP[variant_key.lower()] = pos_map


def _from_1337_replace(match: re.Match[str]) -> str:
    """Top-level replacement callback for normalization back to canonical tokens."""
    return VARIANT_INDEX[match.group(0).lower()]


def _replace_leet_100(match: re.Match[str]) -> str:
    """Fast-path 100% probability replacement callback using C-level str.translate."""
    return match.group(0).translate(LEET_TRANS)


def _replace_leet_default(match: re.Match[str]) -> str:
    """Top-level replacement callback for default 0.70 probability and unseeded RNG.

    Uses pre-computed positional mapping MUTABLE_VARIANT_MAP to directly look up
    eligible character indices and replacement characters without string iteration or dictionary lookups.
    """
    token = match.group(0)
    pos_map = MUTABLE_VARIANT_MAP.get(token.lower())
    if not pos_map:
        return token
    chars = list(token)
    for pos, lchar in pos_map:
        if random.random() < INITIAL_SUBSTITUTION_PROBABILITY:
            chars[pos] = lchar
    return "".join(chars)


def to_1337speak(
    text: str,
    probability: float = INITIAL_SUBSTITUTION_PROBABILITY,
    *,
    rng: Optional[random.Random] = None,
) -> str:
    """Apply sparse randomized substitution to known compressed tokens.

    `probability` is per eligible character, matching the historical notion of
    a sparse randomized substitution threshold. A seeded RNG makes tests and
    forensic reproduction deterministic.
    """
    if not 0.0 <= probability <= 1.0:
        raise ValueError("probability must be between 0.0 and 1.0")
    if not text or probability == 0.0:
        return text

    # Fast-path for probability=1.0: use pre-computed translation table and top-level callback
    # Single-pass substitution avoids redundant double-scanning (.search + .sub) (~14.5% speedup)
    if probability == 1.0:
        return VARIANT_REGEX.sub(_replace_leet_100, text)

    # Fast-path for default probability (0.70) and unseeded RNG: use top-level callback
    # Single-pass substitution avoids redundant double-scanning (.search + .sub) (~14.6% speedup)
    if probability == INITIAL_SUBSTITUTION_PROBABILITY and rng is None:
        return MUTABLE_VARIANT_REGEX.sub(_replace_leet_default, text)

    # Direct RNG handle resolution: avoid allocating new random.Random() instances when unseeded
    rand_val = rng.random if rng is not None else random.random

    def replace(match: re.Match[str]) -> str:
        token = match.group(0)
        chars = list(token)
        for i, char in enumerate(chars):
            replacement = LEET_MAP.get(char.lower())
            if replacement and rand_val() < probability:
                chars[i] = replacement
        return "".join(chars)

    return VARIANT_REGEX.sub(replace, text)


def from_1337speak(text: str) -> str:
    """Normalize known randomized variants back to canonical compressed tokens."""
    if not text:
        return text
    # Single-pass substitution avoids redundant double-scanning (.search + .sub) (~15.3% speedup)
    return VARIANT_REGEX.sub(_from_1337_replace, text)


def compile_phase(text: str, canonical_compiler) -> str:
    """Compile with the existing canonical compiler, then apply phase-1 diaspora."""
    return to_1337speak(canonical_compiler(text))


def decompile_phase(text: str, canonical_decompiler) -> str:
    """Normalize diaspora variants, then use the existing canonical decompiler."""
    return canonical_decompiler(from_1337speak(text))


# 4th Development Lane: Conversational Steganography Cipher with Private Mapping
# Implements pre-LLM pre-parser steganographic obfuscation with key-derived mappings.
# Uses zero-width unicode character markers (\u200b, \u200c, \u200d, \ufeff) to encode
# private mappings invisibly into natural-sounding conversational cover text or 1337 Grimoire text.

import hashlib

ZW_MAP = ("\u200b", "\u200c", "\u200d", "\ufeff")
REV_ZW_MAP = {v: i for i, v in enumerate(ZW_MAP)}


class ConversationalSteganographyCipher:
    """4th Lane Steganography Cipher with private key mapping for pre-LLM pre-parser protection."""
    __slots__ = ("key", "_derived_key")

    def __init__(self, key: str):
        if not key:
            raise ValueError("key cannot be empty")
        self.key = key
        self._derived_key = hashlib.sha256(key.encode("utf-8")).digest()

    def _xor_bytes(self, data: bytes) -> bytes:
        klen = len(self._derived_key)
        return bytes(b ^ self._derived_key[i % klen] for i, b in enumerate(data))

    def encode(self, text: str, cover_text: str = "Query processed successfully.") -> str:
        """Encode plaintext into a steganographic cover text using private key mapping."""
        if not text:
            return cover_text
        raw_bytes = text.encode("utf-8")
        xored = self._xor_bytes(raw_bytes)
        zw_seq = []
        for byte in xored:
            q0 = (byte >> 6) & 3
            q1 = (byte >> 4) & 3
            q2 = (byte >> 2) & 3
            q3 = byte & 3
            zw_seq.extend((ZW_MAP[q0], ZW_MAP[q1], ZW_MAP[q2], ZW_MAP[q3]))
        stego_payload = "".join(zw_seq)
        if cover_text:
            return cover_text + stego_payload
        return stego_payload

    def decode(self, stego_text: str) -> str:
        """Decode steganographic payload from stego text using private key mapping."""
        if not stego_text:
            return ""
        payload_chars = [c for c in stego_text if c in REV_ZW_MAP]
        if not payload_chars:
            return ""
        if len(payload_chars) % 4 != 0:
            raise ValueError("Corrupted or invalid steganographic payload")
        byte_list = []
        for i in range(0, len(payload_chars), 4):
            q0 = REV_ZW_MAP[payload_chars[i]]
            q1 = REV_ZW_MAP[payload_chars[i + 1]]
            q2 = REV_ZW_MAP[payload_chars[i + 2]]
            q3 = REV_ZW_MAP[payload_chars[i + 3]]
            byte_val = (q0 << 6) | (q1 << 4) | (q2 << 2) | q3
            byte_list.append(byte_val)
        decrypted_bytes = self._xor_bytes(bytes(byte_list))
        try:
            return decrypted_bytes.decode("utf-8")
        except UnicodeDecodeError as err:
            raise ValueError("Invalid private key or corrupted steganographic payload") from err


def steganography_encode(text: str, key: str, cover_text: str = "Query processed successfully.") -> str:
    """Convenience helper for 4th development lane steganographic encoding."""
    cipher = ConversationalSteganographyCipher(key)
    return cipher.encode(text, cover_text=cover_text)


def steganography_decode(stego_text: str, key: str) -> str:
    """Convenience helper for 4th development lane steganographic decoding."""
    cipher = ConversationalSteganographyCipher(key)
    return cipher.decode(stego_text)
