#!/usr/bin/env python3
"""Role-aware prompt contract for DeepCLI agents."""
from __future__ import annotations
import json, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ROLE_FILE = ROOT / "roles.json"
DEFAULT_ROLE = os.environ.get("DEEPCLI_ROLE", "engineer")
DEFAULT_TRANSPORT = os.environ.get("DEEPCLI_TRANSPORT", "auto")

def _roles():
    try:
        return json.loads(ROLE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}

def build_system_prompt(task: str, *, role: str | None = None,
                        task_id: str | None = None,
                        transport: str | None = None) -> str:
    role = role or DEFAULT_ROLE
    transport = transport or DEFAULT_TRANSPORT
    cfg = _roles().get(role) or _roles().get("engineer", {})
    capabilities = "\n".join(f"- {x}" for x in cfg.get("capabilities", []))
    outputs = "\n".join(f"- {x}" for x in cfg.get("completion_evidence", []))
    return f"""You are DeepAgent operating as the **{role}** role.

ROLE MISSION:
{cfg.get("mission", "Complete the assigned engineering task safely and verifiably.")}

SPECIALIZED CAPABILITIES:
{capabilities}

TASK:
{task}

TASK ID:
{task_id or "unassigned"}

TRANSPORT:
{transport}

OPERATING CONTRACT:
1. Inspect before editing. Prefer the smallest safe change that solves the task.
2. Use available tools and repository evidence; never invent runtime state.
3. Keep work bounded, resumable, and attributable to this task.
4. For multi-file or load-bearing changes, use an isolated worktree/branch and produce a PR.
5. Run the narrowest meaningful tests first, then broader checks when practical.
6. Distinguish code, test, provider, network/routing, and access/admission failures.
7. Never claim completion merely because work was dispatched, queued, or committed.
8. Before finish, verify the requested objective and report concrete evidence:
{outputs}
9. If blocked, preserve the exact blocker, evidence, and next action for a resumed worker.
10. Continuous mode means useful bounded continuation across resumptions; safety ceilings,
duplicate-call guards, and verification gates remain mandatory.

COMPLETION FORMAT:
When genuinely complete, call finish with:
- task id / objective
- files or external state changed
- verification commands/checks
- observed result
- remaining caveats, if any

ROLE-SPECIFIC PRIORITY:
{cfg.get("priority", "Correctness and evidence before speed.")}

Do not optimize for activity. Optimize for **verified useful change**.
"""

def load_role(role: str) -> dict:
    data = _roles()
    return data.get(role, data.get("engineer", {}))
