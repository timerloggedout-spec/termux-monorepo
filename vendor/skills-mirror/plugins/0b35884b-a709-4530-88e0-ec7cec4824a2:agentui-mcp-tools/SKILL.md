---
name: agentui-mcp-tools
description: Give an AgentUI app its own MCP server — custom tools in `mcp/*.js` written with `defineTool`, plus written playbooks in `mcp/guides/<slug>.md` — so Claude, Cursor or any MCP client can act inside the app as the connected user. Covers both adding tools to an app that already has a UI and building a **standalone MCP server** — an app with no pages whose only job is to be an MCP server. Use when the user wants a custom MCP server, an MCP server of their own, MCP tools, wants their assistant to read or act on their AgentUI app's data, asks to "expose this as a tool" or "make this an MCP", or wants to write the business rules an assistant should follow when using that app. Not for configuring MCP servers someone else published.
---

# Custom MCP tools for an app

Every AgentUI app already exposes generic data tools over MCP (list/get/count per
entity, plus app context). **Custom tools are for the things generic CRUD cannot
express**: a business action, a multi-step calculation, a report, a write guarded by
the app's own rules.

Tools live in the app's own repo, under `mcp/`, and ship with `agentui project push`
like everything else.

## Two shapes, one mechanism

- **Tools on an app that has a UI** — the app is the product; MCP is how an assistant
  reaches into it.
- **A standalone MCP server** — an AgentUI app with **no pages at all**, whose only job
  is to be an MCP server. Entity schemas for the data it owns, `mcp/*.js` for the
  actions, `mcp/guides/*.md` for the judgement. You get a hosted database, per-user
  auth, secrets, file storage and integrations for free, and you never write transport,
  session or token-refresh code.

Build both the same way: `agentui project create --name "…"`, write `entities/` and
`mcp/`, then `agentui project push --yes --build`. If the user asks for "an MCP server"
with no mention of an app, this is the shape to reach for — see ``agentui-ship-app`` for
the create/push/build loop.

One wrinkle for the standalone shape: the structural validator treats an empty `pages/`
as an **error** ("the app has no routes and renders nothing"), because it is written for
apps. On a pure MCP server that finding is expected — say so rather than "fixing" it,
or give the app one trivial landing page so every check stays green.

```text
mcp/
├── summarizeOverdueInvoices.js   → tool_summarize_overdue_invoices
└── guides/
    └── collections.md            → a playbook the assistant reads before acting
```

The tool name is derived from the filename: `summarizeOverdueInvoices` →
`tool_summarize_overdue_invoices` (snake_cased, `tool_` prefix, 64 chars max).

## Writing a tool

Read `agentui skills info mcp-tools` first — it is the platform's live authoring doc and
it moves faster than this file. What follows is the shape, not the specification.

A tool file default-exports `defineTool({...})` from `@/mcp`:

```js
import { defineTool, ToolError } from "@/mcp";
import { Invoice } from "@/entities/Invoice";

export default defineTool({
    description: "Summarize overdue invoices for one customer. Read-only.",
    input: {
        type: "object",
        properties: {
            customerId: { type: "string", description: "Customer record id" },
            days: { type: "number", description: "Minimum days overdue (default 1)" },
        },
        required: ["customerId"],
        additionalProperties: false,
    },
    annotations: { readOnlyHint: true },
    guide: "collections",
    async run({ customerId, days = 1 }, ctx) {
        const LIMIT = 100;
        const cutoff = Date.now() - days * 86_400_000;
        const rows = await Invoice.filter({ customerId, status: "overdue" }, "-dueDate", LIMIT);
        const overdue = rows.filter((r) => new Date(r.dueDate).getTime() <= cutoff);
        if (!overdue.length) {
            throw new ToolError("NO_INVOICES", `No invoices at least ${days} day(s) overdue.`, {
                retryable: false,
            });
        }
        return {
            count: overdue.length,
            total: overdue.reduce((sum, r) => sum + r.amount, 0),
            // Say so when the page was full — a total the assistant reads as
            // complete, but is not, is worse than no total.
            truncated: rows.length === LIMIT,
        };
    },
});
```

What each field is for:

- `description` — **how the assistant chooses this tool over another.** Max 500 chars.
  Say what it does *and when to call it*. A vague description is the single most common
  reason a tool is never used.
- `input` — a plain JSON Schema object. `$id`, `$schema`, `$ref`, `$defs` and
  `definitions` are rejected; keep it self-contained and set `additionalProperties: false`.
- `output` — optional result schema.
- `access` — an app access rule, e.g. `{ user_condition: { role: "admin" } }`. The tool
  is hidden from users who cannot use it.
- `annotations` — `readOnlyHint`, `destructiveHint`, `idempotentHint`. Be honest: a
  client decides whether to confirm with the human based on these.
- `run(args, ctx)` — `ctx` carries `invocationId`, `environment`, `catalogRevision`,
  `deadlineMs`, `env` (app env vars, service keys withheld), `integrations`, `apiKey`.
  Return JSON-serializable data.

## Errors

Throw `ToolError(CODE, message, { retryable, outcome })` for anything the assistant
could act on. The code is `UPPER_SNAKE` (2–64 chars); `outcome` is `"not-started"`,
`"completed"` or `"unknown"`. **Anything else you throw is reported as a generic
`TOOL_ERROR` with the message withheld**, so an un-wrapped error is a dead end for
whoever is calling it.

## Identity and safety

Calls run as the **connected app user** through a short-lived actor session — never as
a service role. `User.me()` inside `run` is that person. So a tool cannot read more
than its caller can, and your access rules and row-level security still apply
(see ``agentui-app-data``).

## Guides

`mcp/guides/<slug>.md` is the one markdown path the CLI pushes into an app. The slug
must be lowercase `[a-z0-9-]`, max 64 chars. Front-matter drives when the assistant
reaches for it:

```markdown
---
title: Collections process
description: How we chase overdue invoices, step by step.
whenToUse:
  - the user asks to chase or escalate an overdue invoice
aliases: [collections]
relatedTools: [tool_summarize_overdue_invoices]
---

## Escalation
7 days: reminder. 30 days: notice.

## Exceptions
Never escalate key accounts.
```

Use a guide for policy and judgement the tools themselves cannot encode.

## Ship and verify

```bash
agentui validate mcp/summarizeOverdueInvoices.js   # name the file explicitly
agentui project push --dry-run
agentui project push --yes --build                 # tools exist only once the app is rebuilt
```

**`agentui validate --all` does not cover `mcp/`.** Its disk scan walks `components/`,
`pages/`, `functions/` and `Layout.jsx` only, so a brand-new tool file is silently
skipped and a clean `--all` means nothing about your tools. Pass the paths yourself.

The manifest is generated by asking the running app, so a broken tool file fails at
manifest time, not at call time. Limits: 100 tools and 100 guides per app, 512 KB of
manifest. If a tool does not show up in the client, rebuild and check
``agentui-troubleshoot``.

## Connecting a client to it

The server is remote HTTP with a bearer credential, minted **per app user and per
environment** — so each person's assistant acts as that person, and staging never
answers with production data. The CLI does not mint it: the user opens the app
(`agentui project open --preview`) and connects their client there. The platform hands
back a ready-made snippet per client, including:

```bash
claude mcp add <server-name> <mcp-url> --transport http --header "Authorization: Bearer <secret>"
```

plus Cursor, Claude Desktop, Windsurf and Codex equivalents. That secret is a live
credential for that user's access to the app — never paste it into a file you push, a
message, or this transcript. Tell the user where to get it and let them run the command.
