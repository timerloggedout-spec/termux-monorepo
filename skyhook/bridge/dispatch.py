"""Build Jules session plans — no API calls (CI-safe)."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional

from .config import BridgeConfig, load_config


@dataclass
class JulesTaskPlan:
    """Structure representing a planned Jules delegation task.

    Attributes:
        title: Title of the task session.
        prompt: Detailed instructions or task prompt.
        source_repo: The repository to clone and run on.
        starting_branch: Initial branch to check out.
        require_plan_approval: If True, pauses for review before running.
    """
    title: str
    prompt: str
    source_repo: str
    starting_branch: str
    require_plan_approval: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Converts the task plan to a dictionary representation."""
        return asdict(self)


def plan_task(
    title: str,
    prompt: str,
    *,
    source_repo: Optional[str] = None,
    starting_branch: Optional[str] = None,
    require_plan_approval: bool = False,
    config: Optional[BridgeConfig] = None,
) -> JulesTaskPlan:
    """Creates a planned Jules task, applying staging redirects if required.

    Args:
        title: Title of the task session.
        prompt: Detailed prompt instruction.
        source_repo: Target repository (defaults to home_repo).
        starting_branch: Starting target branch (defaults to default_branch).
        require_plan_approval: If True, requires interactive plan approval.
        config: Loaded config to resolve defaults from.

    Returns:
        The generated JulesTaskPlan.
    """
    cfg = config or load_config()
    branch = starting_branch or cfg.default_branch
    if cfg.prefer_staging and branch == "master":
        branch = "master-staging"
    return JulesTaskPlan(
        title=title,
        prompt=prompt,
        source_repo=source_repo or cfg.home_repo,
        starting_branch=branch,
        require_plan_approval=require_plan_approval,
    )


def plan_from_task_yaml_fields(
    fields: Dict[str, Any],
    *,
    config: Optional[BridgeConfig] = None,
) -> JulesTaskPlan:
    """Parses and generates a JulesTaskPlan from task queue YAML fields.

    Args:
        fields: A dictionary representing parsed YAML fields.
        config: Loaded config to resolve defaults from.

    Returns:
        The generated JulesTaskPlan.
    """
    return plan_task(
        title=str(fields.get("title") or fields.get("id") or "untitled"),
        prompt=str(fields.get("prompt") or ""),
        source_repo=fields.get("repo"),
        starting_branch=fields.get("branch"),
        require_plan_approval=bool(fields.get("require_plan_approval", False)),
        config=config,
    )
