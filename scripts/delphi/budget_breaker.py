"""E-08 budget circuit breaker, simulated offline (per the matrix:
"E-08 can be simulated offline before any account exists").

A local cap around an invocation callable: calls are counted, the
kill switch trips AT the cap, and every later call is denied before
invocation — overshoot is impossible by construction, and the denied
calls are counted separately so the receipt shows both.
"""

from __future__ import annotations


class BudgetTripped(Exception):
    """Raised when a call is attempted after the local cap tripped."""


class CapGuard:
    def __init__(self, fn, limit: int):
        if limit < 0:
            raise ValueError("limit must be >= 0")
        self._fn = fn
        self.limit = limit
        self.calls = 0
        self.denied = 0

    @property
    def tripped(self) -> bool:
        return self.calls >= self.limit

    def __call__(self, *args, **kwargs):
        if self.tripped:
            self.denied += 1
            raise BudgetTripped(
                f"local budget cap {self.limit} already reached; call denied")
        self.calls += 1
        return self._fn(*args, **kwargs)

    def receipt(self) -> dict:
        return {"schema": "delphi-budget-breaker/v1", "limit": self.limit,
                "calls": self.calls, "denied": self.denied,
                "overshoot": max(0, self.calls - self.limit)}
