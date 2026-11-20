---
name: multi-stage-workflow
description: "Multi-stage workflow orchestrator implementing Search → Analyze → Generate pattern.\nDispatches 3 specialized agents in sequence, passing output from each stage as input\nto the next. Enables complex multi-step code analysis and generation tasks.\n"
argument-hint: "[task description] [@path/to/project] [--model=sonnet|haiku] [--budget=USD]"
allowed-tools: Task, Read, Bash, Glob, Grep
---

# Multi-Stage Workflow

## Overview

Multi-stage workflows decompose complex tasks into 3 sequential stages:
1. **Search** — Grep codebase for patterns, extract entities
2. **Analyze** — Synthesize patterns, identify relationships, extract model
3. **Generate** — Design artifacts (spec.json, architecture, code) incorporating learnings

Each stage is a specialized agent. Output from stage N flows into stage N+1.

## Usage

```bash
/multi-stage-workflow "find cart patterns, analyze, design new cart feature" @./project
/multi-stage-workflow "search for auth middleware, analyze patterns, generate new auth layer" @./src --budget=2.00
```

## How It Works

### Stage 1: Search (Haiku)
- **Goal:** Find relevant code patterns in the codebase
- **Input:** Task description
- **Process:**
  - Grep for entity keywords (cart, item, discount, auth, middleware)
  - Extract file paths and line numbers
  - List all matching entities with context
- **Output:** JSON with:
  ```json
  {
    "stage": "search",
    "query": "cart patterns",
    "patterns_found": [
      {
        "entity": "Cart",
        "files": ["src/models/cart.py"],
        "lines": [10, 50],
        "snippet": "class Cart: ..."
      }
    ],
    "total_matches": 3
  }
  ```

### Stage 2: Analyze (Sonnet)
- **Goal:** Synthesize patterns into a coherent domain model
- **Input:** Search results from Stage 1
- **Process:**
  - Identify common fields across entities
  - Extract relationships (has_many, belongs_to, etc.)
  - Infer data types and constraints
  - Design normalized entity model
- **Output:** JSON with:
  ```json
  {
    "stage": "analyze",
    "entities": [
      {
        "name": "Cart",
        "fields": ["id", "user_id", "total_price"],
        "relationships": [
          {"type": "has_many", "target": "LineItem"}
        ]
      }
    ],
    "relationships": [
      {
        "from": "Cart",
        "to": "LineItem",
        "type": "one_to_many",
        "foreign_key": "cart_id"
      }
    ]
  }
  ```

### Stage 3: Generate (Sonnet)
- **Goal:** Create spec.json and architecture incorporating analysis
- **Input:** Analysis results from Stage 2 + original task description
- **Process:**
  - Generate spec.json with entities, properties, relationships
  - Design database schema with FK columns
  - Outline implementation steps
  - Estimate effort and cost
- **Output:** JSON with:
  ```json
  {
    "stage": "generate",
    "spec": {
      "name": "shopping_cart",
      "entities": [
        {
          "name": "Cart",
          "properties": [
            {"name": "id", "type": "integer", "primary_key": true},
            {"name": "user_id", "type": "integer", "foreign_key": true}
          ]
        }
      ],
      "relationships": [...]
    },
    "cost_estimate": "$0.50",
    "implementation_steps": [...]
  }
  ```

---

## Implementation

You are orchestrating a 3-stage workflow. Follow these steps:

### Phase 1: Initialize Workflow

Extract arguments from `$ARGUMENTS`:
- Position 1: task description (e.g., "find cart patterns...")
- Position 2: @path to project (optional, defaults to current directory)
- Flags: --model, --budget

Initialize tracing:
```python
import json
from datetime import datetime

workflow_id = f"mswf-{datetime.now().isoformat()}"
task_description = "$ARGUMENTS[0]"
project_path = "$ARGUMENTS[1]" or "."

workflow_state = {
    "id": workflow_id,
    "task": task_description,
    "project": project_path,
    "stages": {}
}

print(f"[MSWF] Initialized workflow {workflow_id}")
print(f"[MSWF] Task: {task_description}")
print(f"[MSWF] Project: {project_path}")
```

### Phase 2: Dispatch Stage 1 — Search

**Agent:** Haiku (fast, file-aware searcher)
**Role:** Grep patterns from codebase
**Prompt:**

```
You are a codebase pattern searcher. Your task:

1. Parse the task: "{task_description}"
2. Identify entity keywords (e.g., "cart" → Cart, LineItem, Discount)
3. Grep the project at {project_path} for each keyword
4. Return results as JSON in the exact format specified

Task: {task_description}
Project path: {project_path}

Output ONLY valid JSON (no markdown, no extra text):
{{
  "stage": "search",
  "query": "...",
  "patterns_found": [
    {{
      "entity": "Cart",
      "files": ["path/to/file.py"],
      "lines": [10, 20],
      "snippet": "class Cart: ..."
    }}
  ],
  "total_matches": 3
}}
```

Invoke via Task tool:

```!
from anthropic import Anthropic

client = Anthropic()
search_prompt = '''You are a codebase pattern searcher...
[full prompt above]
'''

response = client.messages.create(
    model="claude-3-5-haiku-20241022",
    max_tokens=2000,
    messages=[
        {"role": "user", "content": search_prompt}
    ]
)

search_result = response.content[0].text
print(search_result)
workflow_state['stages']['search'] = json.loads(search_result)
```

**Gate:** Search returns valid JSON with >= 1 pattern found
- If 0 patterns: ask user to refine query
- If valid JSON: continue to Stage 2

### Phase 3: Dispatch Stage 2 — Analyze

**Agent:** Sonnet (reasoning engine)
**Role:** Synthesize patterns into domain model
**Input:** search_result from Stage 1
**Prompt:**

```
You are a domain model analyzer. You have search results from Stage 1.

Task: Analyze these patterns and synthesize a normalized domain model.

Search results (Stage 1):
{search_result}

Original task: {task_description}

Your job:
1. Identify all entities mentioned
2. Extract common fields across entities
3. Infer relationships (one_to_many, many_to_many, etc.)
4. Design FK columns
5. Identify data type hints from context

Output ONLY valid JSON (no markdown, no extra text):
{{
  "stage": "analyze",
  "entities": [
    {{
      "name": "Cart",
      "fields": ["id", "user_id", "total_price"],
      "inferred_types": {{"id": "integer", "user_id": "integer"}},
      "relationships": [
        {{"type": "has_many", "target": "LineItem"}}
      ]
    }}
  ],
  "relationships": [
    {{
      "from": "Cart",
      "to": "LineItem",
      "type": "one_to_many",
      "foreign_key": "cart_id"
    }}
  ]
}}
```

Invoke via Task tool:

```!
analyze_prompt = f'''You are a domain model analyzer...
[full prompt above with {search_result} injected]
'''

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=3000,
    messages=[
        {"role": "user", "content": analyze_prompt}
    ]
)

analyze_result = response.content[0].text
print(analyze_result)
workflow_state['stages']['analyze'] = json.loads(analyze_result)
```

**Gate:** Analysis returns valid JSON with entity list
- If no entities: loop back and refine search
- If valid: continue to Stage 3

### Phase 4: Dispatch Stage 3 — Generate

**Agent:** Sonnet (design architect)
**Role:** Create spec.json and implementation plan
**Input:** analyze_result from Stage 2
**Prompt:**

```
You are a spec architect. You have a domain model from Stage 2.

Domain model (Stage 2):
{analyze_result}

Original task: {task_description}

Your job:
1. Design spec.json with full entity definitions
2. Add database column definitions with FK constraints
3. Include validation rules
4. Create implementation roadmap
5. Estimate effort and cost

Output ONLY valid JSON (no markdown, no extra text):
{{
  "stage": "generate",
  "spec": {{
    "name": "shopping_cart",
    "version": "1.0.0",
    "entities": [
      {{
        "name": "Cart",
        "properties": [
          {{"name": "id", "type": "integer", "primary_key": true}},
          {{"name": "user_id", "type": "integer", "foreign_key": true}},
          {{"name": "total_price", "type": "float", "nullable": false}}
        ]
      }}
    ]
  }},
  "implementation_steps": [
    "1. Create Cart model with properties",
    "2. Create LineItem model with cart_id FK"
  ],
  "cost_estimate": "$0.50",
  "effort_estimate": "2-4 hours"
}}
```

Invoke via Task tool:

```!
generate_prompt = f'''You are a spec architect...
[full prompt above with {analyze_result} injected]
'''

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=4000,
    messages=[
        {"role": "user", "content": generate_prompt}
    ]
)

generate_result = response.content[0].text
print(generate_result)
workflow_state['stages']['generate'] = json.loads(generate_result)
```

**Gate:** Generation returns valid spec.json
- Check for required keys: entities, properties
- If invalid: retry with refined prompt

### Phase 5: Consolidate & Report

Summarize the 3-stage output:

```python
print("\n[MSWF] Workflow Complete")
print(f"[MSWF] ID: {workflow_id}")
print(f"[MSWF] Stages executed: {len(workflow_state['stages'])}")

for stage_name, stage_output in workflow_state['stages'].items():
    print(f"\n[{stage_name.upper()}]")
    print(json.dumps(stage_output, indent=2))

# Save workflow state
with open(f"{project_path}/.mswf-{workflow_id}.json", "w") as f:
    json.dump(workflow_state, f, indent=2)

print(f"\n[MSWF] Saved state to .mswf-{workflow_id}.json")
```

---

## Error Handling

| Stage | Error | Recovery |
|-------|-------|----------|
| Search | 0 patterns found | Ask user to refine query; retry |
| Search | Invalid JSON | Retry with stricter prompt |
| Analyze | No entities in output | Re-run search with broader keywords |
| Generate | Missing spec.json keys | Retry with explicit schema template |

---

## Testing

Test the workflow end-to-end:

```bash
/multi-stage-workflow "find user patterns, analyze, generate auth model" @./test-project
```

Expected output:
- Stage 1: JSON with patterns_found (>= 1)
- Stage 2: JSON with entities list
- Stage 3: JSON with spec.json + implementation steps

---

## Cost Estimation

- Stage 1 (Haiku): ~$0.02 (fast grep + summarize)
- Stage 2 (Sonnet): ~$0.15 (reasoning over patterns)
- Stage 3 (Sonnet): ~$0.20 (spec design + planning)
- **Total:** ~$0.37 per execution

Use `--budget=1.00` to cap spend.

---

## See Also

- `/one-shot-generate` — Full code generation pipeline (uses this pattern internally)
- `docs/tier35-agentic.md` — Stage-based architecture reference
