---
name: one-shot-generate
description: "End-to-end agentic one-shot. Claude conducts a pipeline of deterministic\nscripts + specialist agents to take a natural-language feature request and\nproduce verified, wired code in the user's existing codebase. Trigger words:\n\"one-shot\", \"generate feature\", \"build feature\", \"add CRUD/API/endpoints\",\n\"add batch job\", \"scaffold\". Accepts an optional ``--templated`` flag that\nfalls back to the legacy Python-only pipeline (no Claude tokens) for users\nwho need free, deterministic generation.\n"
argument-hint: "[task description] [@path/to/project] [--apply] [--templated] [--budget=USD] [--rollback]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Task
---

<!--
  OTel Span Propagation: This skill emits spans for all 9 pipeline stages.
  Spans are exported to Jaeger on localhost:6831 for observability.
  See docs/observability/span-propagation.md for architecture details.
-->

<!--
  AUDITORS: This file is the pipeline dispatcher. The stages live in
  stages/plan.md, stages/build.md, stages/verify.md, stages/ship.md,
  stages/record.md. Claude reads all of them in sequence.
  See AUDIT_ME_FIRST.md at the repo root for orientation.
-->

# One-Shot Generate — Agentic Pipeline

You are conducting the one-shot generation pipeline. The user has invoked
`/one-shot "their feature description" @/path/to/project`. Your job is to
run the pipeline below, spawning specialist agents at the right points,
and ship working code into their project.

The arguments are: `$ARGUMENTS`

---

## Step 0 — Initialize routing trace & route: templated vs agentic (DO THIS FIRST)

Initialize the routing trace (enables introspection into decision layers):

```!
SESSION_ID=$(date +%s)-$(openssl rand -hex 3)
PROJECT_ROOT="$2"  # from @./path argument
python "../one-shot-generator/scripts/routing_trace.py" --init "$SESSION_ID" "$PROJECT_ROOT"
```

Initialize OTel tracer for span propagation across all 9 pipeline stages:

```!
import sys
import os
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from otel_tracer import init_tracer, trace_stage
from trace_context import capture_context, restore_context

# Initialize tracer for this invocation
tracer = init_tracer("one-shot-generate")
print(f"[OTel] Initialized tracer for session {SESSION_ID}")
```

**Route on `--templated`:**

If `$ARGUMENTS` contains `--templated` / `--legacy` / `--free`:

!`python "../one-shot-generator/scripts/one_shot_orchestrator.py" "$ARGUMENTS"`

Log the decision:
```python
from scripts.routing_trace import get_or_create_trace
trace = get_or_create_trace(SESSION_ID, PROJECT_ROOT)
trace.log_decision(
    stage='SKILL.Step0',
    layer='L1_ROUTER',
    decision='route_templated',
    context={'arguments': ARGUMENTS},
    consequence='Use legacy Python pipeline, zero Claude tokens, lower quality'
)
```

Summarise the output and stop. This costs zero Claude tokens but produces
lower-quality code. It is a fallback, not the main path.

**For everything else: continue below (agentic route).**

Log the agentic route decision:
```python
trace.log_decision(
    stage='SKILL.Step0',
    layer='L1_ROUTER',
    decision='route_agentic',
    context={'arguments': ARGUMENTS},
    consequence='Proceed through 5-stage agentic pipeline'
)

---

## Flags (read once, apply throughout)

- `--apply` — Stage 6: mutate project files (default is dry-run)
- `--budget=USD` — Stage 1.5: halt if cost estimate exceeds this
- `--force` — bypass clarification gate even at confidence < 0.55; **also bypasses predictive failure warnings in Stage 0.3**
- `--review` — Stage 2.5: show spec.json to user before agents fire
- `--incremental` — Stage 2.6: one entity per commit
- `--legacy-safe` — Stage 0.7: `legacy_guard.py` caps to 3 files, blocks --apply
- `--no-doubt` — skip Stage 5.5 (DEFAULT ON: doubt-driven adversarial pass)
- `--no-ship-check` — skip Stage 6 ship gates (DEFAULT ON); gates run
  `ship_gates.py` which returns READY or BLOCKED before any --apply
- `--no-adr` — skip ADR emission (Stage 2, `adr_writer.py` writes to docs/adr/)
- `--no-consistency-check` — skip Stage 5.7 (`cross_agent_consistency.py` + `security_deep_scan.py`, DEFAULT ON);
  catches subtle logic bugs that per-agent review misses
- `--require-approval-webhook=URL` — Stage 5.9: POST before wiring
- `--rollback` / `--rollback=true` — Stage 7: enable autonomous rollback on N consecutive failures (default: true, N=3)
- `--rollback=false` — Stage 7: disable rollback, let failures escalate (manual recovery only)

**Productivity-skill integration flags** (skills wired into specific stages):

- `--grill` — force grill-me invocation in Stage 1.6 (otherwise fires only
  when feature description is ambiguous: < 50 chars, 0 entities extracted,
  or extractor confidence < 0.55)
- `--tdd-strict` — Stage 3 routes through tdd-cycle skill (RED → GREEN →
  REFACTOR per entity) instead of parallel implementer + test-author
- `--no-compress` — skip caveman compression of reviewer/critic inputs in
  Stages 5 and 7 (DEFAULT ON when prompt > 8k tokens)
- `--no-systematic-debug` — skip systematic-debug skill in Stage 7 when
  critic hits the same failure twice (DEFAULT ON: forces 6-phase root-cause
  investigation instead of guess-loop)
- `--no-handoff` — skip Stage 8.5 handoff document emission (DEFAULT ON on
  SHIPPED runs)

---

## Pipeline — execute in order

Read and execute each stage file in sequence. Each stage is instrumented with
OTel spans for observability (see `docs/observability/span-propagation.md`).

### PLAN Phase

Stages 0 – 2.7: curriculum check, **predictive failure check (0.3)**, scan & extract, cost gate, **grill-me (1.6)**,
doc lookup, architect, spec review, incremental slice, service-author.

```!
# Stage 0: Curriculum check (curriculum_check span)
with tracer.start_as_current_span("curriculum_check") as span:
    span.set_attribute("stage", "curriculum_check")
    # Executed below via @./stages/plan.md

# Stage 0.3: Predictive failure check (predictive_check span)
with tracer.start_as_current_span("predictive_check") as span:
    span.set_attribute("stage", "predictive_check")
    # Executed below via @./stages/plan.md
```

**PLAN** → `@./stages/plan.md`

### BUILD Phase

Stage 3: implementer × N + test-author (parallel) — or **tdd-cycle**
when `--tdd-strict`.

```!
# Stage 3: Code generation (write_code span)
with tracer.start_as_current_span("write_code") as span:
    span.set_attribute("stage", "write_code")
    span.set_attribute("parallel", True)
    # Executed below via @./stages/build.md
```

**BUILD** → `@./stages/build.md`

### VERIFY Phase

Stages 4 – 5.7: auto-patch, reviewer (with **caveman** compression on
large inputs), doubter, consistency + SAST.

```!
# Stage 4: Verify & patch (verify_and_patch span)
with tracer.start_as_current_span("verify_and_patch") as span:
    span.set_attribute("stage", "verify_and_patch")
    # Executed below via @./stages/verify.md

# Stage 5: Security review (security_review span)
with tracer.start_as_current_span("security_review") as span:
    span.set_attribute("stage", "security_review")
    # Executed below via @./stages/verify.md
```

**VERIFY** → `@./stages/verify.md`

### SHIP Phase

Stages 6 – 7: wire, migrate, approval gate, critic loop (max 3 iter,
with **systematic-debug** triggered on repeat failures).

```!
# Stage 6: Auto-wire main.py (auto_wire_main span)
with tracer.start_as_current_span("auto_wire_main") as span:
    span.set_attribute("stage", "auto_wire_main")
    # Executed below via @./stages/ship.md

# Stage 7: Run tests & critic (run_tests span)
with tracer.start_as_current_span("run_tests") as span:
    span.set_attribute("stage", "run_tests")
    # Executed below via @./stages/ship.md
```

**SHIP** → `@./stages/ship.md`

### RECORD Phase

Stages 8 – 8.5: graph refresh, learnings, dream consolidation,
**handoff** runbook on SHIPPED.

```!
# Stage 8: Record beads & learnings (record_beads span)
with tracer.start_as_current_span("record_beads") as span:
    span.set_attribute("stage", "record_beads")
    # Executed below via @./stages/record.md
```

**RECORD** → `@./stages/record.md`

---

After RECORD completes, give the user a summary:
- Files generated / modified
- Entities and their relationships
- Migration file location (if any)
- Wire plan (what was added to main.py / urls.py)
- Total estimated cost
- Critic verdict (SHIPPED / ESCALATED)

**Emit routing trace summary** (L1 memory introspection):
```python
from scripts.routing_trace import get_or_create_trace
trace = get_or_create_trace(SESSION_ID, PROJECT_ROOT)
summary = trace.emit_summary()
print("\n=== L1 Memory Routing Trace ===")
print(f"Session: {summary['session_id']}")
print(f"Total decisions: {summary['total_decisions']}")
print(f"By layer: {summary['by_layer']}")
print(f"Trace saved: {summary['trace_file']}")
```

Users can inspect `.one-shot/routing_trace.jsonl` to see the exact layer
(L1 Router, L2 Module, L3 Data) that made each decision.

**Emit OTel trace summary** (Observability):
```python
print("\n=== OTel Span Propagation ===")
print(f"Service: one-shot-generate")
print(f"Session ID: {SESSION_ID}")
print(f"Spans emitted for all 9 stages (0–8)")
print(f"Trace available in Jaeger at http://localhost:16686")
print(f"Search for traces with service='one-shot-generate'")
print(f"View span-propagation.md for detailed architecture")
```
