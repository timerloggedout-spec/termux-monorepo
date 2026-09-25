#!/usr/bin/env python3
"""Dependency-free regression tests for RinDig provenance classification."""
from rindig_provenance_audit import classify_state, STATES

def check(pinned, fork, upstream, expected):
    actual = classify_state(pinned, fork, upstream)
    assert actual == expected, (pinned, fork, upstream, actual, expected)

def main():
    check("a", "a", "a", "aligned")
    check("a", "a", "b", "upstream-ahead")
    check("a", "b", "b", "pin-behind")
    check("a", "b", "c", "fork-and-pin-drift")
    check(None, "b", "c", "unresolved")
    assert len(STATES) == 5
    print("rindig provenance classification: PASS")

if __name__ == "__main__":
    main()
