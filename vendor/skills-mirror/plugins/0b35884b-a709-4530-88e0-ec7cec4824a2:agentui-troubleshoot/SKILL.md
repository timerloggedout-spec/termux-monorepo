---
name: agentui-troubleshoot
description: Diagnose an AgentUI app that is failing — validation errors, a push that did not take effect, stale builds, function errors, "project not found", auth problems, recurring runtime errors — and report broken or missing CLI behaviour back to the platform. Use when an agentui command fails, when the live app does not reflect what was pushed, when a function or automation errors, or when the user says the app is broken.
---

# When an AgentUI app misbehaves

Run every command with `--json`: hard errors come back as `{ "error": "...", "details":
... }` on stdout with exit code 1, which is far more actionable than the pretty output.
But **exit 0 is not proof of success** — `validate` reports findings as `valid: false`
and still exits 0, and `push` reports a per-operation `failed` count. Read the payload.

## Order of checks

```bash
agentui auth status                      # logged in? which company? token expiring?
agentui workspace current                # right workspace?
agentui env current && agentui env status   # which environment, and is its build fresh?
agentui project status                   # components/entities vs. last sync
agentui project diff                     # what changed locally since sync
agentui validate --all                   # the platform's own validator
agentui logs invocations                 # failures first, with console output
agentui logs telemetry                   # recurring errors, by frequency
```

## The failures you will actually hit

**"I pushed but the app is unchanged."** Push flags a rebuild; it does not perform one.
Run `agentui build` — `--yes` on production, the same guardrail push has. If the build
half of `push --build` failed, re-running the push will not save you: the code is
already sent, so it reports "Nothing to push" and never rebuilds. Run
`agentui build --yes` on its own. `agentui env status` tells you whether the served
artifact is stale and when it was last built.

**`functions invoke` refuses to run.** The app has unbuilt changes and the function
would execute stale code. Build first, or pass `--allow-stale` on purpose.

**"Project not found" for a project that exists.** In order of likelihood: you passed an
**App id** instead of a workflow id (`<projectId>` is the "Project ID" column of
`agentui project list`); the `.agent.json` is from an old sync; or the authenticated
user is in a different company — check `agentui auth whoami`.

**"No project found. Run 'agentui project sync <id>' first."** You are outside a synced
project directory. `cd` into it, or pass `--project <id>`.

**Some operations pushed and some did not.** Batches (50 ops / 1 MB) fail independently
and the process can still exit 0. Check `failed` and the per-operation results, then
re-push only what failed.

**`deploy` says "Nothing to deploy".** Deploy ships code; with no local code changes it
exits immediately. If you were expecting a settings change to take effect, that needs a
rebuild: `agentui build --yes`.

**Sync aborted on conflicts.** Local edits would be overwritten. Choose `--theirs`,
`--ours`, or `--merge` (writes `<path>.theirs` beside your file so you can diff).

**The AI instructions look wrong.** `AGENTS.md` and friends are written once and never
overwritten after you edit them, so they can describe the platform as it was months ago.
`agentui project instructions --check` exits non-zero when any is stale. A `.theirs`
sidecar means sync parked the platform's copy rather than clobbering your edits — merge,
do not re-sync.

**A validator rule you do not recognise.** `agentui skills info code-validator` — it
stays in sync with what the runtime actually enforces.

**`validate --all` came back clean but a file is broken.** `--all` scans `components/`,
`pages/`, `functions/` and `Layout.jsx` from disk — **not `mcp/`**, and not files outside
those directories. Pass the paths explicitly: `agentui validate mcp/myTool.js`.

## Report it

The moment a command is wrong, missing, or pointed you the wrong way:

```bash
agentui report broken  "integration test times out on an API that answers in 12s"
agentui report missing "no way to list an app's cron schedules"
agentui report unclear "the deploy guide says push first, but push needs a build"
```

`report broken` attaches the last failed invocation automatically — command, error, CLI
version, platform — scrubbed of `--credential`, `--token`, `--password` and anything
shaped like a live key. Add `--expected "<what should have happened>"`; it is the single
most useful line in a report. Identical reports are de-duplicated for 24h and capped at
5/hour, so a suppressed report exits 0 and is not an error.

For product feedback that is not a defect: `agentui feedback "<what you want to say>"`.

Do not invent a workaround and move on silently. Tell the user what you hit, what you did
instead, and that you filed it.
