"""JSON helpers that retain source decimal tokens without binary-float loss."""
from __future__ import annotations

import json
from decimal import Decimal
from typing import Any


class ExactDecimal(Decimal):
    """A Decimal that retains the exact numeric token received on the wire."""

    def __new__(cls, token: str):
        value = super().__new__(cls, token)
        value.raw_token = token
        return value


def dumps_exact(value: Any, *, indent: int = 2, sort_keys: bool = True) -> str:
    """Serialize JSON, emitting ExactDecimal source tokens as unquoted numbers."""
    def encode(item: Any, level: int) -> str:
        if isinstance(item, ExactDecimal):
            return item.raw_token
        if isinstance(item, Decimal):
            if not item.is_finite():
                raise ValueError("non_finite_decimal")
            return str(item)
        if item is None or isinstance(item, (str, bool, int, float)):
            return json.dumps(item, ensure_ascii=True, allow_nan=False)
        if isinstance(item, (list, tuple)):
            if not item:
                return "[]"
            prefix = " " * (indent * (level + 1))
            suffix = " " * (indent * level)
            values = [prefix + encode(child, level + 1) for child in item]
            return "[\n" + ",\n".join(values) + "\n" + suffix + "]"
        if isinstance(item, dict):
            if not item:
                return "{}"
            if any(not isinstance(key, str) for key in item):
                raise TypeError("json_object_keys_must_be_strings")
            keys = sorted(item) if sort_keys else item.keys()
            prefix = " " * (indent * (level + 1))
            suffix = " " * (indent * level)
            values = [
                prefix + json.dumps(key, ensure_ascii=True) + ": " + encode(item[key], level + 1)
                for key in keys
            ]
            return "{\n" + ",\n".join(values) + "\n" + suffix + "}"
        raise TypeError(f"unsupported_json_type:{type(item).__name__}")

    if indent < 0:
        raise ValueError("indent_must_be_non_negative")
    return encode(value, 0)
