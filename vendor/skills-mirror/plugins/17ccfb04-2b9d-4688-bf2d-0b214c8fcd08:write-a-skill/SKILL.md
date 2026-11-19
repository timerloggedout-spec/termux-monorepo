---
name: write-a-skill
description: Skill authoring guide (mattpocock-inspired). Structure a new skill with proper frontmatter, phases, gates, and helper scripts. Includes linting and test scaffolding. Use when curator discovers gaps in the skill registry.
argument-hint: "[skill-name] [--purpose=...] [--phases=N] [--complexity=simple|medium|advanced] [@path/to/plugin]"
allowed-tools: Read, Write, Bash(python *)
---

# Write-A-Skill — Skill Authoring Guide

**Create production-ready skills, not one-off scripts.** This guide structures
new skills with proper frontmatter, phase gates, and test scaffolding.

Follows mattpocock patterns + one-shot-prompting architecture.

## When to Use

1. **Curator discovers gap** — External skill missing from registry; bring it in
2. **Feature request** — New workflow needed; document as a skill
3. **Repeatability** — Script works once; promote to reusable skill
4. **Team onboarding** — Document best practice as executable skill

## Skill Anatomy

Every skill has this structure:

```
skills/[skill-name]/
├── SKILL.md                  ← Main skill definition (100–500 lines)
├── scripts/                  ← Python helpers (optional)
│   └── [script_name].py
├── tests/                    ← Test cases (optional)
│   ├── conftest.py
│   └── test_[skill_name].py
└── fixtures/                 ← Example inputs (optional)
    └── [example_1].txt
```

## Step 1: Define the Skill (SKILL.md)

Every SKILL.md starts with YAML frontmatter, then phases.

### Frontmatter (Required)

```yaml
---
name: [skill-name]
description: [1-2 sentence summary + key benefit]
argument-hint: "[positional args] [@path] [--flags]"
allowed-tools: Read, Write, Bash(python *)
---
```

**Rules:**
- `name`: kebab-case, unique across plugin
- `description`: 1–2 sentences, end with benefit ("prevents X", "enables Y")
- `argument-hint`: Shows user what to pass; optional args in [...], flags after
- `allowed-tools`: List tools the skill is authorized to use (default: all)

Example:
```yaml
---
name: validate-schema
description: JSON schema validation with auto-fixes. Validates against spec,
  suggests corrections for common violations.
argument-hint: "[@schema.json] [@data.json] [--strict] [--auto-fix]"
allowed-tools: Read, Write, Bash(python validate.py)
---
```

### Phase Structure (Required)

Each skill has phases (1–6). Each phase is:

1. **Clear goal** (what gets done)
2. **Instructions** (how to invoke)
3. **Checklist** (gate before next phase)
4. **Blocker** (what stops progress)

Format:

```markdown
## PHASE [N]: [PHASE NAME]

[1-2 sentence goal]

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/[script].py" --phase=[N] --flag=$ARGUMENT`

Output shows:
- [Key output 1]
- [Key output 2]

**Checklist:**
- ✅ [Gate 1]
- ✅ [Gate 2]

**[BLOCKED]** [When to escalate]
```

Example (from tdd-cycle):

```markdown
## PLAN Phase: Align on Behavior

Before writing ANY test, align on observable behaviors.

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/tdd_cycle_enforcer.py" --phase=plan --feature="$FEATURE"`

Output shows:
- Public interfaces affected
- Testable behaviors (prioritized)
- Tracer bullet (first test)

**Checklist:**
- ✅ User confirms priority behavior
- ✅ Test uses only public APIs
- ✅ Behavior is user-facing

**[BLOCKED]** If test couples to implementation → redesign before proceeding.
```

### Integration Points (Optional)

If the skill is part of the pipeline, show where it's invoked:

```markdown
## Integration in one-shot-prompting

**PLAN stage (pre-architect):** Run grill-me on feature description

```bash
/grill-me "add payment processing" @./project --depth=deep
```

**VERIFY stage (post-architect):** Compress verbose spec

```bash
/caveman @./spec.json --preserve-code
```
```

### Checklist at Bottom

Verify the skill is complete:

```markdown
## Skill Checklist

- ✅ Frontmatter has name, description, argument-hint
- ✅ All phases documented (gate + checklist)
- ✅ Helper script exists and is tested
- ✅ Skill tested locally (smoke + integration)
- ✅ Attribution to mattpocock if adapted
```

## Step 2: Write Helper Script (optional)

If the skill does deterministic work, add a Python script:

```python
# skills/[skill-name]/scripts/[script_name].py

"""[Skill name] helper."""

import argparse
import json
import sys
from pathlib import Path

def phase_1(args):
    """Phase 1: [Phase name]."""
    # Implementation
    return {"output": "value"}

def phase_2(args):
    """Phase 2: [Phase name]."""
    # Implementation
    return {"output": "value"}

def main():
    parser = argparse.ArgumentParser(
        description="[Skill description]"
    )
    parser.add_argument("--phase", required=True, choices=["1", "2", "3"])
    parser.add_argument("--feature", required=False)
    parser.add_argument("--cwd", default=".")
    args = parser.parse_args()

    handlers = {
        "1": phase_1,
        "2": phase_2,
        "3": phase_3,
    }

    result = handlers[args.phase](args)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
```

**Rules:**
- Use stdlib only (no pip deps)
- Return JSON (script output is piped to next phase or CLI)
- Support `--phase` argument
- Raise `SystemExit(1)` on failure

## Step 3: Write Tests (optional)

Create test file: `tests/test_[skill_name].py`

```python
"""Tests for [skill name]."""

import subprocess
import json
from pathlib import Path

def test_phase_1_valid_input():
    """PHASE 1: Valid input produces output."""
    result = subprocess.run(
        ["python", "scripts/[script_name].py", "--phase=1", "--feature=test"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert "output" in output

def test_phase_1_missing_arg():
    """PHASE 1: Missing required arg fails gracefully."""
    result = subprocess.run(
        ["python", "scripts/[script_name].py", "--phase=1"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "required" in result.stderr.lower()

def test_all_phases_sequence():
    """Integration: All phases run in sequence."""
    # Phase 1
    result1 = subprocess.run([...], capture_output=True, text=True)
    state1 = json.loads(result1.stdout)

    # Phase 2 (uses output from phase 1)
    result2 = subprocess.run([...], capture_output=True, text=True)
    state2 = json.loads(result2.stdout)

    assert state2["progressed"]
```

## Step 4: Lint & Test

Before committing:

```bash
# Check SKILL.md syntax
python skills/[skill-name]/scripts/lint_skill.py \
  skills/[skill-name]/SKILL.md

# Run tests
pytest skills/[skill-name]/tests/ -v

# Smoke test (manual invocation)
/[skill-name] "test input" @./example
```

## Skill Template (Copy-Paste Start)

```yaml
---
name: [skill-name]
description: [1-2 sentences + benefit]
argument-hint: "[args] [@path] [--flags]"
allowed-tools: Read, Write, Bash(python *)
---

# [Skill Name]

[2-3 sentence overview]

## When to Use

1. [Scenario 1]
2. [Scenario 2]
3. [Scenario 3]

## PHASE 1: [Phase Name]

[Goal]

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/[script].py" --phase=1 --flag=$ARG`

Output shows:
- [Output 1]
- [Output 2]

**Checklist:**
- ✅ [Gate 1]
- ✅ [Gate 2]

**[BLOCKED]** [When to escalate]

---

**Last updated:** 2026-05-19
```

## Example: Real Skill (grill-me)

See `../grill-me/SKILL.md` for a complete example with 6 phases.

## Publishing a Skill

Once tested locally:

```bash
# 1. Update plugin.json version
# 2. Add skill to SKILL_REGISTRY.json (curator tool)
# 3. Update skills/CLAUDE.md with new entry
# 4. Commit: "feat(skills): add [skill-name]"
# 5. Tag release
```

## Attribution

If adapting from mattpocock/skills:

At bottom of SKILL.md, add:

```markdown
---

**Adapted from:** mattpocock/skills ([original skill name])
```

## Checklist

- ✅ Name is kebab-case and unique
- ✅ Description is 1–2 sentences
- ✅ All phases have clear gates
- ✅ Helper script uses stdlib only
- ✅ Tests cover all phases + error cases
- ✅ SKILL.md is <500 lines
- ✅ Script can be run standalone (python script.py)
- ✅ Attribution added (if adapted)
- ✅ Smoke test passes locally
- ✅ CLAUDE.md updated in skills/ directory

**[BLOCKED]** If SKILL.md >500 lines → split into two skills or link to external docs.

---

**Adapted from:** mattpocock/skills (skill authoring pattern)

**Last updated:** 2026-05-19
