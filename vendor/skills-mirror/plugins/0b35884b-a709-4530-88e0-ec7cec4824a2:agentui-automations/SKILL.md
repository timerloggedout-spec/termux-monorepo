---
name: agentui-automations
description: Build scheduled and triggered background jobs for an AgentUI app with `agentui automation` — cron, webhook, incoming email or WhatsApp, running on Deno with access to the app's own data. Use when the user wants something to run every night/hour/Monday, a recurring report, a reminder, a sync job, a webhook receiver, or any work that has to happen without anyone opening the app.
---

# Automations

An automation is a sibling workflow inside the app's container, so it already reaches
the app's data. It lives in the **app's own project folder** — one repo, one PR, one
review.

```text
automations/daily-report/
├── automation.json          ← generated. Do NOT edit by hand.
└── steps/
    ├── 001-fetch-orders.js
    └── 002-send-summary.js
```

**The filename is the structure.** The number is the execution order, renaming the file
renames the step, deleting it deletes the step — along with its run history, which
`push` warns about first. A rename is only recognised as a rename while the contents are
unchanged: push the rename on its own, then edit.

Steps run on **Deno**, so import what you use: `import axios from "npm:axios";` —
axios is not injected; `fetch` is global. A step is either format:

```js
// script: the body of an async function — `return` the output
const { data } = await axios.get(inputs.url);
return { count: data.length };
```

```js
// module: the default export receives { inputs, initialData, stepData, env }
import axios from "npm:axios";
export default async function ({ inputs, env }) {
    const { data } = await axios.get(inputs.url);
    return { count: data.length };
}
```

`pull` lands the platform's code. If that overwrites a file on disk that the lockfile
does not track and whose contents differ, the old file is copied to `<file>.orig` first
and named in the output — check for `.orig` files after a pull and merge anything
you meant to keep.

## The loop

```bash
agentui automation create "Daily report"
# write automations/daily-report/steps/001-fetch.js
agentui automation push --dry-run
agentui automation push
agentui automation trigger set cron "0 9 * * *" --tz America/Mexico_City
agentui automation run --watch          # run it now and print the result
agentui automation logs                 # last run, step by step
```

| Command | What it tells you |
| --- | --- |
| `agentui automation list` | every automation, what fires it, next run, last status |
| `agentui automation pull [name] [--all]` | write the platform's steps to disk |
| `agentui automation show [name] [--step <s>]` | what the platform holds now vs. your local files |
| `agentui automation logs [name] [--list] [--run <id>]` | last run's output, or the run history |
| `agentui automation trigger list\|set\|rm\|incoming` | what fires it, and what step 001 receives |

`trigger incoming` shows the shape of the payload the first step receives — read it
before writing step 001 rather than guessing.

## Before you write a step

- `agentui guide automations` — the live playbook.
- `agentui skills list` — the platform skills a step can use (Send Email, Send WhatsApp,
  Web Request, Web Search, Excel, PDF, OCR, Chat GPT, Database Operations…).
  `agentui skills info "Send Email"` for the exact call.
- Secrets a step needs go through `agentui secrets request <NAME>`, never inline in the
  step file — **but pass `--project <automationId>`**. Run from the app folder it
  defaults to the app's workflow id, and a grant to the app does not reach the sibling
  automation: the step would fail at runtime with the secret visibly "there".
  `agentui automation list --json` gives you the automation's id. Use `--needed` when
  the value is the user's to supply (see ``agentui-ship-app``).

Schedule in the user's timezone, not the server's — always pass `--tz`. And tell the
user what the cron expression means in words before you set it; "0 9 * * *" and
"every Monday at 9" are easy to confuse and the failure is silent for a week.
