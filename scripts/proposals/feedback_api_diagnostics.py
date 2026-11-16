#!/usr/bin/env python3
"""Classify advisory feedback errors; never log tokens or raw GitHub responses."""
from __future__ import annotations
import json
import sys


def classify(status: int, headers: dict[str, str], message: str) -> str:
    """Defer only a proved exhausted installation core quota, not generic 403s."""
    h = {str(k).lower(): str(v).strip() for k, v in headers.items()}
    numeric = ('x-ratelimit-limit', 'x-ratelimit-used', 'x-ratelimit-reset')
    verified = (
        status == 403
        and 'installation' in message.lower()
        and 'api rate limit exceeded' in message.lower()
        and h.get('x-ratelimit-remaining') == '0'
        and h.get('x-ratelimit-resource') == 'core'
        and all(h.get(k, '').isdigit() and len(h[k]) <= 20 for k in numeric)
    )
    if verified:
        verified = (int(h['x-ratelimit-limit']) > 0
                    and int(h['x-ratelimit-used']) >= int(h['x-ratelimit-limit'])
                    and int(h['x-ratelimit-reset']) > 0)
    return 'deferred_rate_limit' if verified else 'error'


def main() -> int:
    data = json.load(sys.stdin)
    print(classify(int(data.get('status', 0)), data.get('headers', {}), str(data.get('message', ''))))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
