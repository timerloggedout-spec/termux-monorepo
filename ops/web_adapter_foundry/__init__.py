"""Web Adapter Foundry — evidence-backed web operation discovery and
adapter synthesis. See docs/ops/WEB-ADAPTER-FOUNDRY.md and
.agents/skills/web-adapter-foundry/SKILL.md."""
from .waf import (VERSION, EVIDENCE_LABELS, EXECUTORS, PROMOTION, PROBES,
                  validate_registry, validate_envelope, plan_probes,
                  can_promote, handle_request, load_catalog, load_registry,
                  load_taxonomy, taxonomy_node, sse_encode, EventBus,
                  PURPOSES, validate_brief, plan_from_brief,
                  parse_issue_form, render_plan_markdown)
from .facade import make_server as make_facade_server

__all__ = ["VERSION", "EVIDENCE_LABELS", "EXECUTORS", "PROMOTION", "PROBES",
           "validate_registry", "validate_envelope", "plan_probes",
           "can_promote", "handle_request", "load_catalog", "load_registry",
           "load_taxonomy", "taxonomy_node", "sse_encode", "EventBus",
           "PURPOSES", "validate_brief", "plan_from_brief",
           "parse_issue_form", "render_plan_markdown", "make_facade_server"]
