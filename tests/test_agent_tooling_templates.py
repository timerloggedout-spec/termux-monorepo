from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.ci.verify_agent_tooling_templates import validate_manifest


def sample():
    candidate = {
        "id": "agent-browser",
        "path": "refTemplates/smods/agent-browser_fork",
        "status": "fork_required",
        "fork_url": "https://github.com/timerloggedout-spec/agent-browser_fork.git",
        "pinned_sha": None,
    }
    manifest = {
        "schema": "agent-toolchain-template/v1",
        "template_id": "vercel-agent-toolchain",
        "status": "discovered",
        "smods_index": "refTemplates/smods/INTEGRATIONS.json",
        "upstreams": [
            {"id": name, "url": f"https://github.com/example/{name}"}
            for name in (
                "agent-browser", "skills-cli", "agent-skills",
                "agent-desktop", "portless", "kitesurf",
            )
        ],
        "smods_candidates": [candidate],
    }
    index = {"entries": [dict(candidate)]}
    return manifest, index, candidate


class AgentToolingTemplateTests(unittest.TestCase):
    def test_fork_required_is_explicit_but_not_a_fake_gitlink(self):
        manifest, index, _ = sample()
        self.assertEqual(validate_manifest(manifest, index, {}, set()), [])

    def test_pinned_requires_matching_gitmodules_and_gitlink(self):
        manifest, index, candidate = sample()
        pinned = dict(candidate, status="pinned", pinned_sha="a" * 40)
        manifest["smods_candidates"] = [pinned]
        index["entries"] = [pinned]
        errors = validate_manifest(
            manifest,
            index,
            {pinned["path"]: pinned["fork_url"]},
            {pinned["path"]},
        )
        self.assertEqual(errors, [])

    def test_pinned_without_gitlink_fails_closed(self):
        manifest, index, candidate = sample()
        pinned = dict(candidate, status="pinned", pinned_sha="b" * 40)
        manifest["smods_candidates"] = [pinned]
        index["entries"] = [pinned]
        errors = validate_manifest(
            manifest,
            index,
            {pinned["path"]: pinned["fork_url"]},
            set(),
        )
        self.assertTrue(any("missing its 160000 gitlink" in error for error in errors))

    def test_manifest_and_smods_index_cannot_drift(self):
        manifest, index, _ = sample()
        index["entries"][0]["path"] = "refTemplates/smods/wrong_fork"
        errors = validate_manifest(manifest, index, {}, set())
        self.assertTrue(any("missing from the global index" in error for error in errors))

    def test_fork_required_cannot_already_be_a_live_submodule(self):
        manifest, index, candidate = sample()
        errors = validate_manifest(
            manifest,
            index,
            {candidate["path"]: candidate["fork_url"]},
            {candidate["path"]},
        )
        self.assertTrue(any("fork_required must not be represented" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
