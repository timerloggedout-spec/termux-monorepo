"""Scope-aware native evaluation gate selection."""
from unittest import TestCase, main

from ml.pipelines.eval_lanes.native import native_gates


class NativeGateScopeTests(TestCase):
    def test_general_work_uses_repository_gate(self):
        self.assertEqual(tuple(g.name for g in native_gates()), ("repo-gate",))

    def test_termux_work_adds_termux_smoke(self):
        self.assertEqual(
            tuple(g.name for g in native_gates(termux_related=True)),
            ("repo-gate", "termux-smoke"),
        )


if __name__ == "__main__":
    main()
