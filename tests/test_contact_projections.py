"""Regression contracts for the explicit Agent Linguist pair registry."""

from __future__ import annotations

from dataclasses import replace
import importlib.util
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "linguist" / "agent_document_pairs.py"
SPEC = importlib.util.spec_from_file_location("agent_document_pairs", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"cannot load Linguist mapper: {SCRIPT}")
agent_document_pairs = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = agent_document_pairs
SPEC.loader.exec_module(agent_document_pairs)

EXPECTED_PAIRS = (
    ("CLAUDE.hum.md", "CLAUDE.md"),
    ("GEMINI.hum.md", "GEMINI.md"),
    (".codex/AGENTS.hum.md", ".codex/AGENTS.md"),
    ("docs/icm/CLAUDE.hum.md", "docs/icm/CLAUDE.md"),
    ("docs/icm/AGENTS.hum.md", "docs/icm/AGENTS.md"),
    ("docs/icm/maintenance/CLAUDE.hum.md", "docs/icm/maintenance/CLAUDE.md"),
    ("docs/icm/maintenance/AGENTS.hum.md", "docs/icm/maintenance/AGENTS.md"),
)
EXPECTED_RELATIONSHIPS = {
    "root-claude": "direct projection",
    "root-gemini": "direct projection",
    "codex-compatibility": "compatibility/tooling surface",
    "icm-claude": "direct projection",
    "icm-agents": "compatibility/tooling surface",
    "icm-maintenance-claude": "direct projection",
    "icm-maintenance-agents": "compatibility/tooling surface",
}
EXPECTED_ALIAS_GROUPS = {
    "icm-machine-aliases": ("icm-claude", "icm-agents"),
    "icm-maintenance-machine-aliases": (
        "icm-maintenance-claude",
        "icm-maintenance-agents",
    ),
}


def registry_pairs() -> tuple[tuple[str, str], ...]:
    return tuple(
        (projection.source.as_posix(), projection.target.as_posix())
        for projection in agent_document_pairs.PAIR_REGISTRY
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
    def test_registry_has_seven_explicit_lane_contracts(self) -> None:
        pairs = registry_pairs()
        self.assertEqual(pairs, EXPECTED_PAIRS)
        self.assertEqual(len({projection.pair_id for projection in agent_document_pairs.PAIR_REGISTRY}), 7)
        self.assertEqual(len({projection.lane for projection in agent_document_pairs.PAIR_REGISTRY}), 7)
        self.assertEqual(
            {projection.pair_id: projection.relationship_class for projection in agent_document_pairs.PAIR_REGISTRY},
            EXPECTED_RELATIONSHIPS,
        )
        self.assertTrue(all(projection.mapping_mode == "identity" for projection in agent_document_pairs.PAIR_REGISTRY))
        for source, target in pairs:
            self.assertTrue(source.endswith(".hum.md"))
            self.assertEqual(target, source.removesuffix(".hum.md") + ".md")

    def test_alias_groups_and_root_historical_provenance_are_explicit(self) -> None:
        groups: dict[str, list[str]] = {}
        for projection in agent_document_pairs.PAIR_REGISTRY:
            if projection.alias_group:
                groups.setdefault(projection.alias_group, []).append(projection.pair_id)
        self.assertEqual({key: tuple(value) for key, value in groups.items()}, EXPECTED_ALIAS_GROUPS)

        root_claude = next(
            projection
            for projection in agent_document_pairs.PAIR_REGISTRY
            if projection.pair_id == "root-claude"
        )
        self.assertEqual(root_claude.historical_aliases, ("AGENTS.hum.md", "AGENTS.md"))
        self.assertEqual(root_claude.historical_alias_relationship_class, "historical rename")
        self.assertIn("Muse initiated the naming migration", root_claude.provenance_note)
        self.assertIn("owner-supplied attribution", root_claude.provenance_note)
        self.assertIn("verification pending", root_claude.provenance_note)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            seed_registry_tree(root)
            misclassified = replace(
                root_claude,
                historical_alias_relationship_class="direct projection",
            )
            registry = (misclassified, *agent_document_pairs.PAIR_REGISTRY[1:])
            with self.assertRaisesRegex(ValueError, "historical aliases require the historical rename class"):
                agent_document_pairs.validate_registry(root, registry)

    def test_identity_projection_preserves_bytes_without_document_wide_leet(self) -> None:
        payload = b"# Human source\r\n1337_$934k remains a literal document token.\r\n"
        projection = agent_document_pairs.PAIR_REGISTRY[0]
        self.assertEqual(agent_document_pairs.render(payload, projection), payload)
        self.assertEqual(agent_document_pairs.render(payload, projection), payload)

    def test_unassigned_mapping_mode_fails_registry_preflight(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            seed_registry_tree(root)
            changed = replace(agent_document_pairs.PAIR_REGISTRY[0], mapping_mode="leet-1337")
            registry = (changed, *agent_document_pairs.PAIR_REGISTRY[1:])
            with self.assertRaisesRegex(ValueError, "unsupported mapping mode"):
                agent_document_pairs.validate_registry(root, registry)

    def test_write_then_check_proves_exact_parity_and_check_does_not_write(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            seed_registry_tree(root)
            self.assertEqual(agent_document_pairs.write_or_check(root, check=False), 0)
            before = {target: (root / target).read_bytes() for _, target in EXPECTED_PAIRS}
            timestamps = {target: (root / target).stat().st_mtime_ns for _, target in EXPECTED_PAIRS}
            self.assertEqual(agent_document_pairs.write_or_check(root, check=True), 0)
            for source, target in EXPECTED_PAIRS:
                self.assertEqual((root / target).read_bytes(), (root / source).read_bytes())
                self.assertEqual((root / target).read_bytes(), before[target])
                self.assertEqual((root / target).stat().st_mtime_ns, timestamps[target])

    def test_alias_divergence_fails_before_any_write_or_check_result(self) -> None:
        for check in (False, True):
            for source_path in (
                "docs/icm/AGENTS.hum.md",
                "docs/icm/maintenance/AGENTS.hum.md",
            ):
                with self.subTest(check=check, source_path=source_path):
                    with tempfile.TemporaryDirectory() as directory:
                        root = Path(directory)
                        seed_registry_tree(root)
                        before = {
                            target: (root / target).read_bytes()
                            for _, target in EXPECTED_PAIRS
                        }
                        (root / source_path).write_bytes(b"# divergent alias\n")
                        with self.assertRaisesRegex(
                            ValueError,
                            "divergent rendered sources.*CLAUDE.hum.md.*AGENTS.hum.md",
                        ):
                            agent_document_pairs.write_or_check(root, check=check)
                        for target, expected in before.items():
                            self.assertEqual((root / target).read_bytes(), expected)

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
            changed = replace(
                agent_document_pairs.PAIR_REGISTRY[0],
                source=Path("../outside.hum.md"),
                target=Path("../outside.md"),
            )
            registry = (changed, *agent_document_pairs.PAIR_REGISTRY[1:])
            with self.assertRaisesRegex(ValueError, "unsafe component|escapes"):
                agent_document_pairs.validate_registry(root, registry)
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
                agent_document_pairs.write_or_check(root, check=False)
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
                agent_document_pairs.write_or_check(alias_root, check=False)

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
                agent_document_pairs.write_or_check(root, check=False)
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
                agent_document_pairs.write_or_check(root, check=False)
            self.assertEqual(target.read_bytes(), original)

    def test_atomic_replace_failure_preserves_prior_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            seed_registry_tree(root)
            target = root / "CLAUDE.md"
            original = target.read_bytes()
            (root / "CLAUDE.hum.md").write_bytes(b"replacement\n")
            with mock.patch.object(agent_document_pairs.os, "replace", side_effect=OSError("simulated")):
                with self.assertRaises(OSError):
                    agent_document_pairs.write_or_check(root, check=False)
            self.assertEqual(target.read_bytes(), original)
            self.assertEqual(list(root.glob(".CLAUDE.md.*.tmp")), [])

    def test_world_writable_target_is_replaced_with_safe_readable_mode(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            seed_registry_tree(root)
            target = root / "CLAUDE.md"
            target.chmod(0o777)
            (root / "CLAUDE.hum.md").write_bytes(b"safe replacement\n")
            self.assertEqual(agent_document_pairs.write_or_check(root, check=False), 0)
            mode = stat.S_IMODE(target.stat().st_mode)
            self.assertEqual(mode, 0o640)
            self.assertFalse(mode & stat.S_IROTH)
            self.assertTrue(mode & stat.S_IRGRP)

    def test_real_repository_pair_parity_and_machine_alias_equality(self) -> None:
        registry = agent_document_pairs.validate_registry(ROOT)
        for projection in registry:
            source_path = ROOT / projection.source
            target_path = ROOT / projection.target
            self.assertEqual(
                target_path.read_bytes(),
                agent_document_pairs.render(source_path.read_bytes(), projection),
            )

        for directory in (ROOT / "docs/icm", ROOT / "docs/icm/maintenance"):
            self.assertEqual((directory / "CLAUDE.md").read_bytes(), (directory / "AGENTS.md").read_bytes())
            self.assertEqual((directory / "CLAUDE.hum.md").read_bytes(), (directory / "AGENTS.hum.md").read_bytes())

    def test_each_agent_source_states_siglary_name_mapping(self) -> None:
        expected_phrases = (
            "The notation system's name of record is **Siglary**",
            "CAVEMAN-MICRO-DENSE-V2.md",
            "Caveman Micro Dense 🧬 v2",
            "Caveman",
            "CEDRLang",
            "prior art",
        )
        for projection in agent_document_pairs.validate_registry(ROOT):
            source = (ROOT / projection.source).read_text(encoding="utf-8")
            with self.subTest(lane=projection.lane):
                for phrase in expected_phrases:
                    self.assertIn(phrase, source)

    def test_root_route_includes_reconnaissance_and_fa_ade_markers(self) -> None:
        source = (ROOT / "CLAUDE.hum.md").read_text(encoding="utf-8")
        for marker in (
            "context-relationship-reconnaissance.md",
            ".agents/skills/context-relationship-graph/SKILL.md",
            "verified evidence",
            "scored **candidates**",
            "Fully Automated Agentic Development",
            "auto-promote",
            "dual gates",
            "BIUDL",
        ):
            self.assertIn(marker, source)

    def test_root_active_routes_remain_agent_specific(self) -> None:
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


if __name__ == "__main__":
    unittest.main()
