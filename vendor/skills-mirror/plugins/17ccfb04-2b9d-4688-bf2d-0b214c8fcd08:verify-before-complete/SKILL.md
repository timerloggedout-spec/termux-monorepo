---
name: verify-before-complete
description: Completion gate. Run fresh verification before claiming done. Syntax → Tests → Lint gates. NO completion claims without status:CLEAR. Blocks "done", "complete", "finished" claims. Essential for Superpowers methodology.
argument-hint: "[@path/to/project] [--gate=syntax|tests|lint|all] [--block-on-warn]"
allowed-tools: Bash(python *)
---

# Verify Before Completion

**Superpowers Rule:** You may NOT claim "done", "complete", "finished", or "ready to use" until ALL verification gates return `status: CLEAR`.

## Run Verification

Run fresh verification gates:

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/completion_gate.py" --gate=all --cwd "$PROJECT_PATH"`

Output structure:
```json
{
  "overall_status": "CLEAR" | "WARN" | "BLOCKED",
  "gates_passed": ["syntax", "tests", ...],
  "gates_warned": ["lint"],
  "gates_blocked": [],
  "blocking_issues": [],
  "gate_results": [...]
}
```

---

## Individual Gates

### Syntax Gate
Validate code syntax across all files:
!`python "${CLAUDE_PLUGIN_ROOT}/scripts/completion_gate.py" --gate=syntax --cwd "$PROJECT_PATH"`

### Tests Gate
Auto-detect test runner (pytest/jest/go test/mvn) and run full suite:
!`python "${CLAUDE_PLUGIN_ROOT}/scripts/completion_gate.py" --gate=tests --cwd "$PROJECT_PATH"`

### Lint Gate
Run security, linting, type coverage checks:
!`python "${CLAUDE_PLUGIN_ROOT}/scripts/completion_gate.py" --gate=lint --cwd "$PROJECT_PATH"`

---

## Results Interpretation

- **CLEAR** — All gates passed. Safe to claim completion.
- **WARN** — Gates passed but found warnings (unused imports, etc.). User must acknowledge.
- **BLOCKED** — Gates failed. Must fix before claiming completion.

---

## Superpowers Rule

**YOU CANNOT OUTPUT:**
- "done"
- "complete"
- "finished"
- "ready to use"
- "all set"
- Any synonym implying success

**UNTIL** `overall_status == "CLEAR"` in the JSON output above.

---

**Paired with:** execute-plan (auto-invoked before final completion)
