"""Dispatch planning helpers — build Jules session requests without calling the API.

Actual HTTP/MCP calls stay out of CI. Agents with JULES_API_KEY can wire
callers later (JULES-ADE-06).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional

from .config import BridgeConfig, load_config


@dataclass
class JulesTaskPlan:
    """One planned Jules session (serializable)."""

    title: str
    prompt: str
    source_repo: str
    starting_branch: str
    require_plan_approval: bool = False

    def to_dict(self) -> Dict[str, Any]:
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
    """Build a task plan targeting HOME defaults."""
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
    """Map tasks/*.yaml style fields into a JulesTaskPlan."""
    return plan_task(
        title=str(fields.get("title") or fields.get("id") or "untitled"),
        prompt=str(fields.get("prompt") or ""),
        source_repo=fields.get("repo"),
        starting_branch=fields.get("branch"),
        require_plan_approval=bool(fields.get("require_plan_approval", False)),
        config=config,
    )
