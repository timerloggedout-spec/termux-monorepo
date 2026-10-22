"""Web Adapter Foundry — evidence-backed web operation discovery and
adapter synthesis. See docs/ops/WEB-ADAPTER-FOUNDRY.md and
.agents/skills/web-adapter-foundry/SKILL.md."""
from .waf import (VERSION, EVIDENCE_LABELS, EXECUTORS, PROMOTION, PROBES,
                  validate_registry, validate_envelope, plan_probes,
                  can_promote, handle_request, load_catalog, load_registry)

__all__ = ["VERSION", "EVIDENCE_LABELS", "EXECUTORS", "PROMOTION", "PROBES",
           "validate_registry", "validate_envelope", "plan_probes",
           "can_promote", "handle_request", "load_catalog", "load_registry"]
