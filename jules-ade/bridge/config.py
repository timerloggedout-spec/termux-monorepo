"""Environment contract for Jules ADE bridge (stdlib only)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class BridgeConfig:
    """Resolved config. API keys are never printed by doctor."""

    jules_api_key_present: bool
    home_repo: str
    default_branch: str
    package_branch: str
    prefer_staging: bool

    @property
    def can_dispatch_jules(self) -> bool:
        return self.jules_api_key_present


def _key_present() -> bool:
    for name in ("JULES_API_KEY", "GOOGLE_JULES_API_KEY"):
        val = os.environ.get(name, "").strip()
        if val:
            return True
    return False


def load_config(
    home_repo: Optional[str] = None,
    default_branch: Optional[str] = None,
) -> BridgeConfig:
    """Load bridge config from env with safe defaults for HOME monorepo."""
    return BridgeConfig(
        jules_api_key_present=_key_present(),
        home_repo=home_repo
        or os.environ.get("JULES_ADE_HOME_REPO", "timerloggedout-spec/termux-monorepo"),
        default_branch=default_branch
        or os.environ.get("JULES_ADE_DEFAULT_BRANCH", "master-staging"),
        package_branch=os.environ.get("JULES_ADE_PACKAGE_BRANCH", "feature/jules-ade"),
        prefer_staging=os.environ.get("JULES_ADE_PREFER_STAGING", "1") not in ("0", "false", "False"),
    )
