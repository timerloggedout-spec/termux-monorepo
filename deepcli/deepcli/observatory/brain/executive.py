"""Executive intent normalization; goals and constraints carry no execution authority."""
from __future__ import annotations
from typing import Any, Mapping

def normalize_intent(intent: Mapping[str, Any]) -> dict[str, Any]:
    goal = str(intent.get("goal", "")).strip()
    if not goal:
        raise ValueError("intent requires a non-empty goal")
    priority = intent.get("priority", 3)
    if isinstance(priority, bool) or not isinstance(priority, int) or not 0 <= priority <= 5:
        raise ValueError("intent priority must be an integer from 0 through 5")
    constraints = sorted({str(item).strip() for item in intent.get("constraints", []) if str(item).strip()})
    success = sorted({str(item).strip() for item in intent.get("success_criteria", []) if str(item).strip()})
    return {"schema_version": "brain.intent.v1", "goal": goal, "priority": priority,
            "constraints": constraints, "success_criteria": success}
