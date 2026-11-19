---
name: run-queue
description: "Create and run an autonomous overnight task queue. Use when the user asks to \"run tasks overnight\", \"queue up work\", \"create an overnight queue\", \"batch these tasks\", \"run this while I sleep\", or wants to execute a list of coding tasks sequentially using the local Claude CLI without supervision.\n"
metadata:
  version: "0.1.0"
---

# Run Queue

Set up and execute a YAML task queue using the local Claude CLI. Each task runs sequentially, commits to the target branch, and logs output. Completed tasks are tracked so re-runs skip finished work.

## Queue File Format

Create a YAML file with this structure:

```yaml
version: "1"
tasks:
  - id: unique-kebab-case-id
    priority: P0
    repo: backend
    estimated_minutes: 20
    prompt: |
      Detailed instructions for Claude. Include:
      - Exact file paths to modify
      - What to change and why
      - How to test (test commands)
      - Commit message to use
```

## Running the Queue

```bash
nohup bash devops/cloud-coder/run-local-overnight.sh devops/cloud-coder/overnight-queue.yaml > /tmp/overnight.log 2>&1 &
```

## Key Rules

- Always use `< /dev/null` on claude invocations to prevent stdin consumption
- Do NOT use `set -e` in the runner (non-zero exits should not kill the loop)
- Tasks run sequentially to avoid merge conflicts
- Completed task IDs persist in `logs/completed.txt` for idempotent reruns
