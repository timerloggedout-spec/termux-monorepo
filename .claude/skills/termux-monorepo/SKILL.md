```markdown
# termux-monorepo Development Patterns

> Auto-generated skill from repository analysis

## Overview

This skill teaches the core development patterns and workflows used in the `termux-monorepo` repository, a Python-based codebase with a modular, script-driven architecture. You'll learn about file naming, import/export conventions, commit patterns, and how to extend the CI pipeline with new gates. This guide is designed to help contributors quickly align with the project's standards and automate common tasks.

## Coding Conventions

### File Naming

- All files use **kebab-case** (lowercase, hyphens as separators).
  - **Example:** `my-script.py`, `data-processor.py`

### Import Style

- Use **relative imports** within modules.
  - **Example:**
    ```python
    from .utils import parse_config
    ```

### Export Style

- Use **named exports** (explicitly define what is exported).
  - **Example:**
    ```python
    def run_task():
        pass

    __all__ = ['run_task']
    ```

### Commit Patterns

- Commits are freeform, often prefixed with `archw1z`.
- Average commit message length: 55 characters.
  - **Example:**  
    ```
    archw1z: add runtime smoke test for new gate
    ```

## Workflows

### Add New Gate to CI Pipeline

**Trigger:** When introducing a new automated gate/checkpoint in the CI pipeline for quality or runtime verification.  
**Command:** `/add-gate`

**Steps:**

1. **Implement the Gate Logic**
   - Write the gate as a script (typically in Python or Bash).
   - Place it in `scripts/ci/{gate_name}.py`.
   - **Example:**
     ```python
     # scripts/ci/runtime-smoke.py
     def main():
         print("Running runtime smoke test...")
         # ...test logic...

     if __name__ == "__main__":
         main()
     ```

2. **Add a CI Workflow**
   - Create a new workflow YAML file in `.github/workflows/{gate_name}.yml`.
   - Configure it to run the new script as part of CI.
   - **Example:**
     ```yaml
     # .github/workflows/runtime-smoke.yml
     name: Runtime Smoke Test
     on: [push, pull_request]
     jobs:
       smoke-test:
         runs-on: ubuntu-latest
         steps:
           - uses: actions/checkout@v3
           - name: Run Smoke Test
             run: python scripts/ci/runtime-smoke.py
     ```

3. **Document the Gate**
   - Add a markdown file in `docs/{GATE_NAME}.md` describing the gate, its purpose, and how it works.
   - **Example:**
     ```
     # Runtime Smoke Gate

     This gate ensures that the runtime environment is healthy...
     ```

4. **Update Architectural Documentation**
   - Update `docs/ARCHW1Z-GATE.md` to reflect the new gate's position and role in the CI pipeline.

## Testing Patterns

- **Test Framework:** Not explicitly detected.
- **Test File Pattern:** Files matching `*.test.*` are considered test files.
  - **Example:** `utils.test.py`, `api-handler.test.py`
- **Best Practice:** Place test files alongside the code they test, using the `.test.` infix.

## Commands

| Command    | Purpose                                                        |
|------------|----------------------------------------------------------------|
| /add-gate  | Scaffold a new CI gate: script, workflow, and documentation.   |
```
