"""Regression contracts for the explicit Agent Linguist pair registry."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "cedrlang" / "render_contact_projections.py"
SPEC = importlib.util.spec_from_file_location("contact_projections", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"cannot load Linguist mapper: {SCRIPT}")
contact_projections = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = contact_projections
SPEC.loader.exec_module(contact_projections)

EXPECTED_PAIRS = (
    ("CLAUDE.hum.md", "CLAUDE.md"),
    ("GEMINI.hum.md", "GEMINI.md"),
    (".codex/AGENTS.hum.md", ".codex/AGENTS.md"),
    ("docs/icm/CLAUDE.hum.md", "docs/icm/CLAUDE.md"),
    ("docs/icm/AGENTS.hum.md", "docs/icm/AGENTS.md"),
    ("docs/icm/maintenance/CLAUDE.hum.md", "docs/icm/maintenance/CLAUDE.md"),
    ("docs/icm/maintenance/AGENTS.hum.md", "docs/icm/maintenance/AGENTS.md"),
)


def registry_pairs() -> tuple[tuple[str, str], ...]:
    return tuple(
        (projection.source.as_posix(), projection.target.as_posix())
        for projection in contact_projections.PAIR_REGISTRY
    )


def seed_registry_tree(root: Path, *, target_bytes: bytes = b"old output\n") -> None:
    for source, target in registry_pairs():
        source_path = root / source
        target_path = root / target
        source_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_bytes(b"# safe fixture\n")
        target_path.write_bytes(target_bytes)


class PairRegistryTests(unittest.TestCase):
    def test_registry_has_exact_seven_unique_sibling_pairs(self) -> None:
        pairs = registry_pairs()
        self.assertEqual(pairs, EXPECTED_PAIRS)
        sources, targets = zip(*pairs)
        self.assertEqual(len(set(sources)), 7)
        self.assertEqual(len(set(targets)), 7)
        for source, target in pairs:
            self.assertTrue(source.endswith(".hum.md"))
            self.assertEqual(target, source.removesuffix(".hum.md") + ".md")

    def test_projection_is_deterministic_lossless_identity(self) -> None:
        payload = b"# Human source\r\n\r\nExact bytes stay intact: SG001-SG008.\r\n"
        source = Path("docs/example.hum.md")
        first = contact_projections.render(payload, source)
        second = contact_projections.render(payload, source)
        self.assertEqual(first, payload)
        self.assertEqual(second, first)

    def test_write_then_check_proves_exact_parity_and_check_does_not_write(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            seed_registry_tree(root)
            self.assertEqual(contact_projections.write_or_check(root, check=False), 0)
            before = {
                target: (root / target).read_bytes()
                for _, target in EXPECTED_PAIRS
            }
            timestamps = {
                target: (root / target).stat().st_mtime_ns
                for _, target in EXPECTED_PAIRS
            }
            self.assertEqual(contact_projections.write_or_check(root, check=True), 0)
            for source, target in EXPECTED_PAIRS:
                self.assertEqual((root / target).read_bytes(), (root / source).read_bytes())
                self.assertEqual((root / target).read_bytes(), before[target])
                self.assertEqual((root / target).stat().st_mtime_ns, timestamps[target])

    def test_cli_check_reports_stale_pair_without_rewriting_it(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            seed_registry_tree(root)
            expected = (root / "CLAUDE.hum.md").read_bytes()
            stale = b"stale output\n"
            (root / "CLAUDE.md").write_bytes(stale)
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--root", str(root), "--check"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("CLAUDE.md", result.stderr)
            self.assertEqual((root / "CLAUDE.md").read_bytes(), stale)
            self.assertEqual((root / "CLAUDE.hum.md").read_bytes(), expected)

    def test_path_escape_fails_before_any_target_write(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            seed_registry_tree(root)
            before = {(root / target).read_bytes() for _, target in EXPECTED_PAIRS}
            unsafe_registry = (
                contact_projections.Projection(Path("../outside.hum.md"), Path("../outside.md")),
                *contact_projections.PAIR_REGISTRY[1:],
            )
            with self.assertRaisesRegex(ValueError, "unsafe component|escapes"):
                contact_projections.validate_registry(root, unsafe_registry)
            after = {(root / target).read_bytes() for _, target in EXPECTED_PAIRS}
            self.assertEqual(after, before)
            self.assertFalse((root.parent / "outside.md").exists())

    def test_symlink_target_is_rejected_before_any_target_write(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            seed_registry_tree(root)
            victim = root / "GEMINI.md"
            victim.unlink()
            victim.symlink_to(root / "CLAUDE.md")
            with self.assertRaises(ValueError):
                contact_projections.write_or_check(root, check=False)
            self.assertEqual((root / "CLAUDE.md").read_bytes(), b"old output\n")

    def test_symlink_repository_root_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            actual_root = base / "repo"
            actual_root.mkdir()
            seed_registry_tree(actual_root)
            alias_root = base / "alias"
            alias_root.symlink_to(actual_root, target_is_directory=True)
            with self.assertRaises(ValueError):
                contact_projections.write_or_check(alias_root, check=False)

    def test_credential_like_source_is_rejected_before_any_target_write(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            seed_registry_tree(root)
            targets = {target: (root / target).read_bytes() for _, target in EXPECTED_PAIRS}
            credential_fixture = "ghp_" + ("A" * 35)
            (root / "GEMINI.hum.md").write_text(
                f"Unsafe credential fixture: {credential_fixture}\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                contact_projections.write_or_check(root, check=False)
            for target, old_bytes in targets.items():
                self.assertEqual((root / target).read_bytes(), old_bytes)

    def test_named_token_assignment_is_rejected_before_any_target_write(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            seed_registry_tree(root)
            target = root / "CLAUDE.md"
            original = target.read_bytes()
            (root / "CLAUDE.hum.md").write_text(
                "GITHUB_TOKEN=abcdefghijklmnopqrstuvwxyz123456789\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                contact_projections.write_or_check(root, check=False)
            self.assertEqual(target.read_bytes(), original)

    def test_atomic_replace_failure_preserves_prior_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            seed_registry_tree(root)
            target = root / "CLAUDE.md"
            original = target.read_bytes()
            (root / "CLAUDE.hum.md").write_bytes(b"replacement\n")
            with mock.patch.object(contact_projections.os, "replace", side_effect=OSError("simulated")):
                with self.assertRaises(OSError):
                    contact_projections.write_or_check(root, check=False)
            self.assertEqual(target.read_bytes(), original)
            self.assertEqual(list(root.glob(".CLAUDE.md.*.tmp")), [])

    def test_real_repository_pair_parity_and_icm_alias_equality(self) -> None:
        for source, target in EXPECTED_PAIRS:
            source_path = ROOT / source
            target_path = ROOT / target
            self.assertTrue(source_path.is_file(), source)
            self.assertTrue(target_path.is_file(), target)
            self.assertEqual(target_path.read_bytes(), contact_projections.render(source_path.read_bytes(), Path(source)))

        for directory in (ROOT / "docs/icm", ROOT / "docs/icm/maintenance"):
            self.assertEqual((directory / "CLAUDE.md").read_bytes(), (directory / "AGENTS.md").read_bytes())
            self.assertEqual((directory / "CLAUDE.hum.md").read_bytes(), (directory / "AGENTS.hum.md").read_bytes())

    def test_active_root_routing_uses_agent_specific_human_sources(self) -> None:
        claude = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        gemini = (ROOT / "GEMINI.md").read_text(encoding="utf-8")
        codex = (ROOT / ".codex/AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("CLAUDE.hum.md", claude)
        self.assertIn("GEMINI.hum.md", gemini)
        self.assertIn("AGENTS.hum.md", codex)
        for icm_route in (
            "docs/icm/CLAUDE.hum.md",
            "docs/icm/CLAUDE.md",
            "docs/icm/AGENTS.hum.md",
            "docs/icm/AGENTS.md",
            "docs/icm/maintenance/CLAUDE.hum.md",
            "docs/icm/maintenance/CLAUDE.md",
            "docs/icm/maintenance/AGENTS.hum.md",
            "docs/icm/maintenance/AGENTS.md",
        ):
            self.assertIn(icm_route, claude)
        self.assertNotIn("AGENTS.md", gemini)
        self.assertNotIn("root `AGENTS.md`", claude)
        self.assertNotIn("Read `AGENTS.md` first", claude)

    def test_authored_agent_docs_exclude_legacy_root_alias_route(self) -> None:
        # Root AGENTS.md was explicitly retired as an active routing surface.
        claude = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        gemini = (ROOT / "GEMINI.md").read_text(encoding="utf-8")
        self.assertNotIn("root `AGENTS.md`", claude)
        self.assertNotIn("Read `AGENTS.md` first", claude)
        self.assertNotIn("AGENTS.md", gemini)


if __name__ == "__main__":
    unittest.main()
