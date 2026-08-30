#!/usr/bin/env python3
"""Validate the cross-file notation-set contract used by PR #390.

This is intentionally read-only: it validates proposal/source/test alignment and
never rewrites generated documentation. It is suitable for CI and local review.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs/proposals/active/notation-sets/source.md"
ITEMS = ROOT / "docs/proposals/active/notation-sets/ITEMS.md"
MDX = ROOT / "proposals/notation-sets.mdx"
TEST = ROOT / "tests/test_notation_sets.py"


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise SystemExit(f"missing {label}: {needle}")


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    items = ITEMS.read_text(encoding="utf-8")
    mdx = MDX.read_text(encoding="utf-8")
    test = TEST.read_text(encoding="utf-8")

    for issue in ("#320", "#309", "#182", "#175", "#126", "#304", "#196", "#177", "#208", "#274"):
        require(source + items + mdx, issue, "required issue reference")

    for nse in ("NSE-019", "NSE-020", "NSE-021"):
        require(items, nse, "ITEMS registry entry")
        require(mdx, nse, "public proposal index entry")

    require(source, "f ; g", "generic diagrammatic composition")
    require(source, "m \\gg= f", "Haskell Monad bind")
    require(source, "defined only when the relevant exponential exists", "exponential existence condition")
    require(items, "Monadic bind", "domain-qualified Haskell bind")
    require(test, 'encoding="utf-8"', "UTF-8 proposal reads")
    require(test, '"#175"', "#175 test reference")
    require(test, '"product"', "product taxonomy")
    require(test, '"F:C:D"', "canonical functor IR")
    require(mdx, "PR 390", "latest revision pointer")

    print("notation-sets contract: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
