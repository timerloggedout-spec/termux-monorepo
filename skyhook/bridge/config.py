"""Environment contract for skyhook (stdlib only)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class BridgeConfig:
    """Configuration contract representing the skyhook execution environment.

    Attributes:
        jules_api_key_present: A boolean indicating if JULES_API_KEY is defined.
        home_repo: The primary repository identifier (owner/repo).
        default_branch: The branch used as the default target branch.
        package_branch: The developer integration branch.
        prefer_staging: If True, rewrites bare 'master' to staging branch.
    """
    jules_api_key_present: bool
    home_repo: str
    default_branch: str
    package_branch: str
    prefer_staging: bool

    @property
    def can_dispatch_jules(self) -> bool:
        """Indicates whether Jules can be dispatched based on credentials."""
        return self.jules_api_key_present


def _key_present() -> bool:
    """Helper that returns True if any variant of the Jules API key is present."""
    for name in ("JULES_API_KEY", "GOOGLE_JULES_API_KEY"):
        if os.environ.get(name, "").strip():
            return True
    return False


def load_config(
    home_repo: Optional[str] = None,
    default_branch: Optional[str] = None,
) -> BridgeConfig:
    """Loads and initializes the skyhook configuration from environment variables.

    Args:
        home_repo: Override for the home repository.
        default_branch: Override for the default target branch.

    Returns:
        A loaded BridgeConfig instance.
    """
    return BridgeConfig(
        jules_api_key_present=_key_present(),
        home_repo=home_repo
        or os.environ.get("SKYHOOK_HOME_REPO", "timerloggedout-spec/termux-monorepo"),
        default_branch=default_branch
        or os.environ.get("SKYHOOK_DEFAULT_BRANCH", "master-staging"),
        package_branch=os.environ.get("SKYHOOK_PACKAGE_BRANCH", "feature/skyhook"),
        prefer_staging=os.environ.get("SKYHOOK_PREFER_STAGING", "1") not in ("0", "false", "False"),
    )
