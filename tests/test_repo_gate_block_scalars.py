"""Block-scalar correctness for the structural YAML check in scripts/ci/repo_gate.py.

`yaml_structure_faults()` tracks block scalar bodies so that shell/JS payload and
JSON-pasted escapes inside a `run: |` are never mistaken for YAML structure.
Tracking them correctly is subtle in three ways, and each of these was a real
defect in the first cut of the check:

  * a payload line that looks exactly like a header (`payload: |`) is *content*;
    re-examining it as a header reported the line after it as under-indented body,
    a false positive that failed the HARD check on a valid schema;
  * a block scalar may be *empty*; the next mapping entry is then a sibling, not a
    lost body — the same false positive, on a different shape;
  * content that dedents below the indentation the first content line established,
    while still indenting past the header, is a *partial* dedent YAML rejects — a
    false negative, which is exactly the blind spot the check exists to close.

Every fixture below is pinned against a real parser wherever one is installed, so
the rule cannot drift away from what YAML actually accepts. The rest of the check
(fault classes for the whole repository, scope, and the gate integration) lives in
tests/test_repo_gate_workflow_yaml.py.
"""

from __future__ import annotations

import importlib.util
import sys
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "ci" / "repo_gate.py"
SPEC = importlib.util.spec_from_file_location("repo_gate", MODULE_PATH)
repo_gate = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = repo_gate
SPEC.loader.exec_module(repo_gate)

try:  # optional oracle: the gate itself must never depend on it
    import yaml
except ImportError:  # pragma: no cover - exercised on a bare Termux install
    yaml = None


def faults(source: str) -> list[str]:
    return repo_gate.yaml_structure_faults(textwrap.dedent(source))


# --------------------------------------------------------------------------- #
# Positive fixtures: the shapes the check used to miss
# --------------------------------------------------------------------------- #

# fix-on-failure.yml shape: content that dedents below the indentation the first
# content line established, while still indenting past the header. Comparing only
# against the header indent cannot see it.
#   ParserError: while parsing a block mapping
PARTIAL_DEDENT_IN_BLOCK_SCALAR = """\
    name: fix-on-failure
    on: [workflow_run]
    jobs:
      fix:
        runs-on: ubuntu-latest
        steps:
          - name: fix
            run: |
                echo first
              echo second
    """

# An indentation indicator counts from the parent node, so the `- ` sequence marker
# shifts the column it is measured from: `|4` under a key at column 4 needs column 8,
# not column 6.
#   ParserError: while parsing a block mapping
INDICATOR_DEEPER_THAN_BODY = """\
    name: ind
    on: [push]
    jobs:
      build:
        runs-on: ubuntu-latest
        steps:
          - run: |4
              echo ok
    """

POSITIVE_FIXTURES = {
    "partial dedent inside a block scalar": (
        PARTIAL_DEDENT_IN_BLOCK_SCALAR,
        "partial dedent",
    ),
    "block scalar shallower than its indentation indicator": (
        INDICATOR_DEEPER_THAN_BODY,
        "indentation indicator",
    ),
}

# --------------------------------------------------------------------------- #
# True negatives: valid YAML the broken tracking rejected
# --------------------------------------------------------------------------- #

# A payload line that looks exactly like another header. It is literal text, so the
# line after it is payload too — not under-indented body content.
BLOCK_SCALAR_PAYLOAD_THAT_LOOKS_LIKE_A_HEADER = """\
    name: schema
    on: [push]
    jobs:
      build:
        runs-on: ubuntu-latest
        env:
          description: |
            payload: |
            next: value
    """

# An empty scalar. This parses as {'description': '', 'type': 'object'}: the next
# mapping entry is a sibling, not the scalar's body.
EMPTY_BLOCK_SCALAR_BEFORE_A_SIBLING = """\
    name: schema
    on: [push]
    jobs:
      build:
        runs-on: ubuntu-latest
        env:
          description: |
          type: object
    """

# An explicit indentation indicator the body satisfies: under a key at column 2,
# `|2` asks for column 4 and the body sits at column 4.
EXPLICIT_INDENTATION_INDICATOR_SATISFIED = """\
    name: ind
    on: [push]
    env:
      SCRIPT: |2
        echo ok
    """

NEGATIVE_FIXTURES = {
    "literal sequence scalar": "items:\n  - |\n    rollback: set flag: false\n",
    "folded root sequence scalar": "- >\n  rollback: set flag: false\n",
    "sequence scalar explicit indentation": "items:\n  - |2\n    rollback: set flag: false\n",
    "explicit indentation permits deeper blank": "run: |2\n    \n  echo ok\n",
    "multiline double quoted escape": 'value: "first\n  second\\n more"\n',
    "multiline single quoted escape": "value: 'first\n  second\\n more'\n",
    "leading blank matching content": "run: |\n  \n  echo ok\n",
    "block scalar payload that looks like a header": (
        BLOCK_SCALAR_PAYLOAD_THAT_LOOKS_LIKE_A_HEADER
    ),
    "empty block scalar before a sibling entry": EMPTY_BLOCK_SCALAR_BEFORE_A_SIBLING,
    "explicit indentation indicator satisfied": EXPLICIT_INDENTATION_INDICATOR_SATISFIED,
    "empty literal scalar before a document end": "description: |\n\n...\n",
    "empty folded scalar before a document end comment": "description: >-\n... # end\n",
    "empty sequence scalar before a document end": "- run: |\n\n...\n",
    "empty scalar before a new document": "description: |\n---\nnext: value\n",
}


class BlockScalarFaultTests(unittest.TestCase):
    def test_each_new_breakage_is_detected(self) -> None:
        for name, (source, expected) in POSITIVE_FIXTURES.items():
            with self.subTest(fixture=name):
                found = faults(source)
                self.assertTrue(found, f"{name}: expected a fault, got none")
                self.assertTrue(
                    any(expected in fault for fault in found),
                    f"{name}: no fault mentioned {expected!r}: {found}",
                )

    def test_near_misses_produce_no_faults(self) -> None:
        for name, source in NEGATIVE_FIXTURES.items():
            with self.subTest(fixture=name):
                self.assertEqual(faults(source), [], f"{name}: unexpected fault")


class BlockScalarScanTests(unittest.TestCase):
    """The scan itself, so a regression names the property it broke."""

    def test_over_indented_leading_blank_is_rejected(self) -> None:
        # Do not dedent: textwrap strips whitespace-only lines, erasing the defect.
        source = "run: |\n    \n  echo ok\n"
        found = repo_gate.yaml_structure_faults(source)
        self.assertTrue(any("leading blank" in fault for fault in found), found)
        if yaml is not None:
            with self.assertRaises(yaml.YAMLError):
                list(yaml.safe_load_all(source))

    def test_quote_state_closes_before_later_unquoted_escape(self) -> None:
        source = 'value: "first\n  second\\n more"\nnext: value\\n trailing\n'
        found = faults(source)
        self.assertEqual(len(found), 1, found)
        self.assertIn("line 3", found[0])

    def test_scalar_payload_is_never_re_examined_as_a_header(self) -> None:
        lines = [
            "env:",
            "  description: |",
            "    payload: |",
            "    next: value",
            "  type: object",
        ]
        inside, found = repo_gate.block_scalar_scan(lines)
        self.assertEqual(inside, {2, 3})
        self.assertEqual(found, [])

    def test_an_empty_scalar_before_a_sibling_is_not_a_lost_body(self) -> None:
        self.assertEqual(
            repo_gate.block_scalar_scan(["description: |", "type: object"]),
            (set(), []),
        )

    def test_document_markers_after_empty_scalars_are_not_body_content(self) -> None:
        for marker in ("...", "---", "... # end", "--- # next"):
            with self.subTest(marker=marker):
                self.assertEqual(
                    repo_gate.block_scalar_scan(["description: |", "", marker]),
                    (set(), []),
                )

    def test_marker_lookalikes_still_report_a_lost_body(self) -> None:
        for marker in ("....", "---oops", "...oops"):
            with self.subTest(marker=marker):
                found = repo_gate.block_scalar_scan(["description: |", marker])[1]
                self.assertEqual(len(found), 1, found)
                self.assertIn("block scalar body", found[0])

    def test_a_partial_dedent_is_reported_once(self) -> None:
        found = repo_gate.block_scalar_scan(["run: |", "    first", "  second", "next: 1"])[1]
        self.assertEqual(len(found), 1, found)
        self.assertIn("partial dedent", found[0])

    def test_an_indentation_indicator_counts_from_the_key_column(self) -> None:
        # `- run: |2` starts at column 2, so its key is at column 4 and the body must
        # reach column 6 — not 4, which measuring from the leading whitespace accepts.
        shallow = ["steps:", "  - run: |2", "    echo ok"]
        found = repo_gate.block_scalar_scan(shallow)[1]
        self.assertEqual(len(found), 1, found)
        self.assertIn("indentation indicator", found[0])
        deep_enough = ["steps:", "  - run: |2", "      echo ok"]
        self.assertEqual(repo_gate.block_scalar_scan(deep_enough)[1], [])

    def test_a_flush_left_body_still_terminates_the_scalar(self) -> None:
        # The property the root-level rule depends on: an escaped heredoc body is not
        # scalar content, so the offending lines stay eligible for reporting.
        inside, _ = repo_gate.block_scalar_scan(["    run: |", "      body", "flush-left", "      more"])
        self.assertEqual(inside, {1})
        self.assertNotIn(2, inside)


@unittest.skipUnless(yaml is not None, "PyYAML not installed; agreement oracle unavailable")
class PyYamlBlockScalarAgreementTests(unittest.TestCase):
    """A rule may only fire on YAML a real parser rejects, and must fire there."""

    @staticmethod
    def _parses(source: str) -> bool:
        try:
            # YAML document-start markers can legally end an empty scalar and
            # begin another document; consume the stream to validate every one.
            list(yaml.safe_load_all(source))
        except Exception:
            return False
        return True

    def test_fixtures_agree_with_a_real_parser(self) -> None:
        for name, (source, _) in POSITIVE_FIXTURES.items():
            with self.subTest(fixture=name):
                text = textwrap.dedent(source)
                self.assertFalse(
                    self._parses(text), f"{name}: fixture is valid YAML, it must not be"
                )
                self.assertTrue(faults(source), f"{name}: rules missed a broken fixture")
        for name, source in NEGATIVE_FIXTURES.items():
            with self.subTest(fixture=name):
                text = textwrap.dedent(source)
                self.assertTrue(
                    self._parses(text), f"{name}: fixture must be valid YAML to be a negative"
                )
                self.assertEqual(faults(source), [], f"{name}: false positive")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
