# REVIEW REQUIRED — do this first

Before any edit, produce `PLAN.md` in the worktree enumerating:

1. Which line ranges of `core.py` move to which module
2. Which names stay in `core.py` (public surface)
3. Every import `core.py` needs after the split
4. Cycle risks and how they are broken
5. Verification checklist (import smoke + tests + dry-run)

Then `finish` with the PLAN. Do NOT proceed to edits until reviewed.

---

[SYSTEM]
You have access to these tools. To CALL a tool, emit EXACTLY one or more blocks of this exact form (no markdown fences, no prose alongside):

<tool_call>{"name": "<tool_name>", "arguments": {<json>}}</tool_call>

Rules:
- Output ONLY <tool_call> block(s) when calling tools.
- If no tool is needed, answer normally in text.
- Multiple <tool_call> blocks allowed (one per line).
- Arguments MUST be valid JSON.

Available tools:

- feedback: Submit GOOD/BAD/None feedback + optional comment + category for an assistant message. category only meaningful when rating=BAD. Args: rating, message_id (optional, defaults to last assistant), category (optional), content (optional).
  schema: {"type": "object", "properties": {"rating": {"type": "string", "enum": ["GOOD", "BAD", "NONE", "LIKE", "DISLIKE"]}, "message_id": {"type": "integer"}, "category": {"type": "string", "enum": ["task-result", "instruction-following", "product-interaction", "service-stability", "resource-cost", "security-privacy-permission", "other"]}, "content": {"type": "string"}}, "required": ["rating"]}
- gh: Run a GitHub CLI command. argv = list of gh args.
  schema: {"type": "object", "properties": {"argv": {"type": "array", "items": {"type": "string"}}}, "required": ["argv"]}
- run: Run a shell command on Termux. First argv element in allowlist.
  schema: {"type": "object", "properties": {"argv": {"type": "array", "items": {"type": "string"}}, "cwd": {"type": "string"}, "idle_timeout_s": {"type": "integer"}, "hard_timeout_s": {"type": "integer"}}, "required": ["argv"]}
- read_file: Read a file under $HOME.
  schema: {"type": "object", "properties": {"path": {"type": "string"}, "max_bytes": {"type": "integer"}}, "required": ["path"]}
- write_file: Write to a file under $HOME/.deepcli, $HOME/deepcli/tasks, or $HOME/deepcli/agent_workspaces.
  schema: {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}, "mode": {"type": "string", "enum": ["text", "base64"]}}, "required": ["path", "content"]}
- list_dir: List entries in a directory under $HOME.
  schema: {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}
- glob: Glob a pattern under a base dir.
  schema: {"type": "object", "properties": {"path": {"type": "string"}, "glob": {"type": "string"}}, "required": ["path", "glob"]}
- list_skills: List installed skills.
  schema: {"type": "object", "properties": {}}
- read_skill: Read a skill's SKILL.md and its files.
  schema: {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}
- logs_sync: Push ~/.deepcli/logs/* to the repo via Git tree API.
  schema: {"type": "object", "properties": {}}
- gh_get_file: Fetch a file from a GitHub repo. Returns {path, sha, size, content} where content is the DECODED text. Use THIS instead of gh api ... --jq .content + b64_decode. Args: repo='owner/name', path='.github/workflows/x.yml', ref='master'.
  schema: {"type": "object", "properties": {"repo": {"type": "string"}, "path": {"type": "string"}, "ref": {"type": "string"}}, "required": ["repo", "path"]}
- gh_edit_file: Surgical edit of a repo file. Fetches, applies each {old,new} replacement (each 'old' must appear exactly once), pushes. Use this INSTEAD of gh_get_file+gh_put when you only need to change a few lines. Args: repo, path, edits=[{old,new}], message, branch (default master).
  schema: {"type": "object", "properties": {"repo": {"type": "string"}, "path": {"type": "string"}, "edits": {"type": "array", "items": {"type": "object", "properties": {"old": {"type": "string"}, "new": {"type": "string"}}, "required": ["old", "new"]}}, "message": {"type": "string"}, "branch": {"type": "string"}, "create_if_missing": {"type": "boolean"}}, "required": ["repo", "path", "edits"]}
- gh_worktree: Manage git worktrees for PR-based changes. Actions: (1) action='create' branch=<name> base=master -> makes ~/.deepcli/worktrees/<branch>; edit files there; (2) action='commit_push_pr' branch=<name> message=<commit msg> title=<pr title> body=<pr body> -> commit, push, open PR; (3) action='remove' branch=<name> -> clean up; (4) action='list'. Use this for multi-file changes or anything needing a local test run; use gh_edit_file for tiny single-file fixes.
  schema: {"type": "object", "properties": {"action": {"type": "string", "enum": ["create", "commit_push_pr", "remove", "list"]}, "branch": {"type": "string"}, "base": {"type": "string"}, "message": {"type": "string"}, "title": {"type": "string"}, "body": {"type": "string"}, "repo": {"type": "string"}, "draft": {"type": "boolean"}, "force": {"type": "boolean"}}, "required": ["action"]}
- gh_put: Commit a file to a GitHub repo via API. Handles base64 + existing sha detection automatically. Use THIS instead of shelling out to base64/curl. Args: repo='owner/name', path='.github/workflows/x.yml', content='<full file text>', message='<commit msg>', branch='master'.
  schema: {"type": "object", "properties": {"repo": {"type": "string"}, "path": {"type": "string"}, "content": {"type": "string"}, "message": {"type": "string"}, "branch": {"type": "string"}}, "required": ["repo", "path", "content"]}
- b64_decode: Decode a base64 string to UTF-8 text. Use after gh api ... --jq .content to get the file body. Args: data='<base64>'.
  schema: {"type": "object", "properties": {"data": {"type": "string"}}, "required": ["data"]}
- finish: Call when done. Pass 'summary'. No tool calls after.
  schema: {"type": "object", "properties": {"summary": {"type": "string"}}, "required": ["summary"]}

[CONVERSATION]
You are mid-task on a refactor. State:

WORKTREE: /data/data/com.termux/files/home/.deepcli/worktrees/refactor-split-agent-deepagent
PACKAGE:  $WORKTREE/deepcli/recapitulation
SOURCE:   $WORKTREE/deepcli/deepagent.py (the direct loop) and $WORKTREE/deepcli/agent.py (the HTTP loop)

ALREADY DONE (do NOT rewrite):
  recapitulation/__init__.py    (301 B)
  recapitulation/runtime.py     (4602 B)
  recapitulation/retry.py       (2313 B)
  recapitulation/lint.py        (freshly copied in — verify it looks right)
  recapitulation/edit.py        (freshly copied in — verify it looks right)

STILL TO DO, in order:
  1. Write $PACKAGE/tools.py        — extract TOOLS, DISPATCH, REQUIRED, execute, _log_tool_error from deepagent.py
  2. Write $PACKAGE/loop.py         — extract _chat_once, loop, __main__ block from deepagent.py
  3. Write $PACKAGE/http_loop.py    — extract the HTTP-hop loop body from agent.py
  4. Rewrite $WORKTREE/deepcli/deepagent.py as a SHIM:
       from recapitulation.loop import loop, execute, TOOLS, DISPATCH  # noqa: F401
       from recapitulation.loop import loop as _loop_main
       if __name__ == "__main__": _loop_main()
  5. Rewrite $WORKTREE/deepcli/agent.py as a shim importing recapitulation.http_loop

CONSTRAINTS:
  - EVERY write_file path MUST start with /data/data/com.termux/files/home/.deepcli/worktrees/refactor-split-agent-deepagent/
  - DO NOT write to /data/data/com.termux/files/home/deepcli/tasks/ (that is scratch, not deliverable)
  - DO NOT write to /data/data/com.termux/files/home/deepcli/ (that is live; protected)
  - Each new file must be <= 400 lines
  - Move symbols; do not duplicate

WHEN ALL 5 ARE DONE:
  cd $WORKTREE
  git add -A
  gh_worktree action=commit_push_pr branch=refactor/split-agent-deepagent message="refactor: split agent core into recapitulation package" title="refactor(deepcli): extract agent.py + deepagent.py into recapitulation/" body="Splits the two monolithic loops into a package. Shims at original paths preserve all imports. See task file modularize-core.md" draft=true

FINISH with a REAL summary like:
  finish(summary='{"pkg":"recapitulation","files_added":8,"shims":2,"loc_max":N,"branch":"refactor/split-agent-deepagent","pr":"<url>"}')

Do NOT finish until the PR is open. Do NOT use a placeholder summary.