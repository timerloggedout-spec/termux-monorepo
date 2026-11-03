"""Errors (ledger row 7).

One primary exception type, presented cleanly: it names the offending
value, the expected contract, and the fix. Execution errors are never
swallowed into a plausible-looking state.
"""


class LabbookError(Exception):
    """Primary labbook exception.

    Messages follow the row-7 shape: offending value · expected contract ·
    fix. Construct with those three parts whenever they are known.
    """

    def __init__(self, message, value=None, expected=None, fix=None):
        parts = [message]
        if value is not None:
            parts.append(f"offending value: {value!r}")
        if expected is not None:
            parts.append(f"expected: {expected}")
        if fix is not None:
            parts.append(f"fix: {fix}")
        super().__init__(" | ".join(parts))
        self.value = value
        self.expected = expected
        self.fix = fix


class IntegrityError(LabbookError):
    """Stored bytes do not match their recorded SHA-256 (verify-on-read)."""


class MissingBytesError(LabbookError):
    """A pointer/record names bytes the CAS does not hold. Fails loudly,
    by hash (ledger row 1 / §2.3 durability rule)."""
