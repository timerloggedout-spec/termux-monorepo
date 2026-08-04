"""Offline unit tests for skyhook.bridge (stdlib only)."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bridge.config import BridgeConfig, load_config  # noqa: E402
from bridge.dispatch import JulesTaskPlan, plan_from_task_yaml_fields, plan_task  # noqa: E402


class TestLoadConfig(unittest.TestCase):
    def test_defaults(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            # clear=True drops inherited env; restore only what we need absent
            cfg = load_config()
        self.assertEqual(cfg.home_repo, "timerloggedout-spec/termux-monorepo")
        self.assertEqual(cfg.default_branch, "master-staging")
        self.assertEqual(cfg.package_branch, "feature/skyhook")
        self.assertTrue(cfg.prefer_staging)
        self.assertIsInstance(cfg.jules_api_key_present, bool)

    def test_env_overrides(self) -> None:
        env = {
            "SKYHOOK_HOME_REPO": "org/other",
            "SKYHOOK_DEFAULT_BRANCH": "dev",
            "SKYHOOK_PACKAGE_BRANCH": "feature/x",
            "SKYHOOK_PREFER_STAGING": "0",
        }
        with mock.patch.dict(os.environ, env, clear=False):
            cfg = load_config()
        self.assertEqual(cfg.home_repo, "org/other")
        self.assertEqual(cfg.default_branch, "dev")
        self.assertEqual(cfg.package_branch, "feature/x")
        self.assertFalse(cfg.prefer_staging)

    def test_key_present_jules(self) -> None:
        with mock.patch.dict(os.environ, {"JULES_API_KEY": "secret-value"}, clear=False):
            cfg = load_config()
        self.assertTrue(cfg.jules_api_key_present)
        self.assertTrue(cfg.can_dispatch_jules)
        # must never embed the secret in repr of bool path
        self.assertNotIn("secret-value", repr(cfg))

    def test_key_present_google_alias(self) -> None:
        env = {"JULES_API_KEY": "", "GOOGLE_JULES_API_KEY": "other-secret"}
        with mock.patch.dict(os.environ, env, clear=False):
            cfg = load_config()
        self.assertTrue(cfg.jules_api_key_present)

    def test_key_absent(self) -> None:
        env = {"JULES_API_KEY": "", "GOOGLE_JULES_API_KEY": ""}
        with mock.patch.dict(os.environ, env, clear=False):
            cfg = load_config()
        self.assertFalse(cfg.jules_api_key_present)
        self.assertFalse(cfg.can_dispatch_jules)


class TestPlanTask(unittest.TestCase):
    def _cfg(self, **kwargs: object) -> BridgeConfig:
        base = dict(
            jules_api_key_present=False,
            home_repo="timerloggedout-spec/termux-monorepo",
            default_branch="master-staging",
            package_branch="feature/skyhook",
            prefer_staging=True,
        )
        base.update(kwargs)
        return BridgeConfig(**base)  # type: ignore[arg-type]

    def test_prefer_staging_rewrites_master(self) -> None:
        plan = plan_task("t", "p", starting_branch="master", config=self._cfg())
        self.assertEqual(plan.starting_branch, "master-staging")

    def test_prefer_staging_off_keeps_master(self) -> None:
        plan = plan_task(
            "t", "p", starting_branch="master", config=self._cfg(prefer_staging=False)
        )
        self.assertEqual(plan.starting_branch, "master")

    def test_defaults_to_config_branch(self) -> None:
        plan = plan_task("t", "p", config=self._cfg())
        self.assertEqual(plan.starting_branch, "master-staging")
        self.assertEqual(plan.source_repo, "timerloggedout-spec/termux-monorepo")

    def test_explicit_repo_and_branch(self) -> None:
        plan = plan_task(
            "title",
            "prompt body",
            source_repo="org/r",
            starting_branch="feature/x",
            require_plan_approval=True,
            config=self._cfg(),
        )
        self.assertEqual(plan.title, "title")
        self.assertEqual(plan.prompt, "prompt body")
        self.assertEqual(plan.source_repo, "org/r")
        self.assertEqual(plan.starting_branch, "feature/x")
        self.assertTrue(plan.require_plan_approval)

    def test_to_dict(self) -> None:
        plan = JulesTaskPlan("a", "b", "o/r", "master-staging")
        d = plan.to_dict()
        self.assertEqual(d["title"], "a")
        self.assertEqual(d["starting_branch"], "master-staging")


class TestPlanFromYamlFields(unittest.TestCase):
    def test_mapping(self) -> None:
        cfg = BridgeConfig(
            jules_api_key_present=False,
            home_repo="timerloggedout-spec/termux-monorepo",
            default_branch="master-staging",
            package_branch="feature/skyhook",
            prefer_staging=True,
        )
        plan = plan_from_task_yaml_fields(
            {
                "id": "SKYHOOK-99",
                "title": "Example",
                "prompt": "do the thing",
                "repo": "timerloggedout-spec/termux-monorepo",
                "branch": "master",
                "require_plan_approval": True,
            },
            config=cfg,
        )
        self.assertEqual(plan.title, "Example")
        self.assertEqual(plan.prompt, "do the thing")
        self.assertEqual(plan.starting_branch, "master-staging")  # rewritten
        self.assertTrue(plan.require_plan_approval)

    def test_id_fallback_title(self) -> None:
        cfg = BridgeConfig(
            jules_api_key_present=False,
            home_repo="timerloggedout-spec/termux-monorepo",
            default_branch="master-staging",
            package_branch="feature/skyhook",
            prefer_staging=True,
        )
        plan = plan_from_task_yaml_fields({"id": "ONLY-ID", "prompt": "x"}, config=cfg)
        self.assertEqual(plan.title, "ONLY-ID")


if __name__ == "__main__":
    unittest.main()
