---
name: fix
description: Apply AEOTester AI SEO fixes in the current repo - JSON-LD schema markup, llms.txt, robots.txt AI crawler rules, Content Signals, meta and social tags, heading hierarchy, language and viewport tags. Shows a diff and asks before writing anything, then re-audits to show the score change.
argument-hint: "[check-id ...] [--yes]"
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, AskUserQuestion, Bash(node --version), Bash(node ${CLAUDE_PLUGIN_ROOT}/skills/audit/scripts/audit.mjs:*), Bash(node ${CLAUDE_PLUGIN_ROOT}/skills/fix/scripts/page-facts.mjs:*), Bash(node ${CLAUDE_PLUGIN_ROOT}/skills/fix/scripts/generate-llms-txt.mjs:*)
---

# AEOTester fix

Fixes the problems `/aeotester:audit` found, in the site's source files.

## Other hosts (Codex, ChatGPT)

The commands below start with Claude Code's plugin-root variable. A host that does not substitute it (Codex, ChatGPT) leaves it as literal text: replace that prefix with the absolute path of the plugin root, which is the folder two levels above the folder that contains this SKILL.md (it holds `skills/`). Do the same for the skill-folder variable, which is the folder that contains this SKILL.md. Write the resolved path into the command; never run it with the variable unexpanded. Slash commands such as `/aeotester:audit` are Claude Code syntax: elsewhere the user asks for this skill by name or mention, and `$ARGUMENTS` means whatever folder, URL or flags their request names (leave it out if there are none). The scripts need Node 18+ and a shell, so the skill only works in a host that can run them.

## Non-negotiable rules

1. **Diff first, then ask.** Before the first Edit or Write, print every planned change as a unified diff in your reply and get the user's approval. `--yes` in the arguments means the user approved in advance: you skip the question, never the diffs. Print them first, then apply.
2. **Never commit, push, stash or change git state.** Never delete files.
3. **Only touch files inside the current repo.** Never edit build output (`dist/`, `_site/`, `out/`, `.next/`, Hugo's `public/`). Fix the source that produces it.
4. **Never invent facts.** Names, people, job titles, credentials, prices, ratings, dates, addresses and social profiles come from the repo (`page-facts.mjs`) or from the user. If a fix needs a fact you do not have, ask, or skip that fix and say why.
5. **Policy choices belong to the user:** which AI bots to allow, and the Content-Signal values (search, ai-input, ai-train). Propose a default and ask.
6. **No network calls.**
7. **Reference only assets that exist.** An `og:image`, logo or icon URL must point at a file in the repo (check with Glob) or one the page already uses.
8. **Tools:** read files (recipes included) with Read, find them with Glob and Grep. Use Bash only for the `node` commands below, written exactly as shown (in Claude Code, an unquoted plugin path) so they match the pre-approved commands. Other shell commands may be denied, and a denied command does not mean `node` is unavailable.

## Steps

### 1. Audit

Check `node --version` (Node 18+ needed). Then run:

```bash
node ${CLAUDE_PLUGIN_ROOT}/skills/audit/scripts/audit.mjs . --no-report --json -
```

Note the score as `total / available` (for example 71/127): `available` already leaves out checks that do not apply. Read `site.mode` and `site.stack.id`:

- `report-only` (WordPress and other CMSs): stop. Content lives in the database; point the user to the fix list in `aeotester-report.md` (run `/aeotester:audit` first if it is missing). Do not edit files.
- `needs-build`: ask whether to run the build command from `site.notes`. Only build if they agree, then audit again.
- `nextjs`: every fix is assisted. Show the diffs as proposals and apply only the ones the user explicitly approves. Never use `--yes` shortcuts for Next.js.
- `full`: continue.

### 2. Choose what to fix

- With check ids in the arguments: fix exactly those, auto or assisted.
- Without: every check where `fixable` is `auto` and `lost` > 0, sorted by points lost. Skip `inconclusive` checks unless the finding is concrete.
- List assisted checks that lost points at the end, as "needs your input", with the command to run them (`/aeotester:fix content.author`). Do not attempt them unasked.
- Advice is not a fix list: checks with status `advice` (Content Signals) and `advice` entries cost no points and may be deliberate. Mention them once at the end as optional, with the command to apply one (`/aeotester:fix ai-access.content-signals`). Do not apply them unasked.
- Never touch pages listed in `excludedPages`: they are kept out of search on purpose and were not scored. Do not remove their noindex or add schema, Open Graph or Twitter tags to them.

### 3. Gather facts and recipes

```bash
node ${CLAUDE_PLUGIN_ROOT}/skills/fix/scripts/page-facts.mjs . [--pages file1.html,file2.html]
```

For each chosen check, open its recipe with the Read tool: `${CLAUDE_SKILL_DIR}/references/fix-recipes/<check-id>.md`. Read every recipe for a check you are about to fix and follow it; read only those. For llms.txt, draft with:

```bash
node ${CLAUDE_PLUGIN_ROOT}/skills/fix/scripts/generate-llms-txt.mjs .
```

Review the draft before proposing it: drop weak lines (for example "Click here to learn more"), keep links useful.

### 4. Find the source

For static HTML the flagged file is the source. For generated sites (Astro, Hugo, Eleventy, Vite, Next.js), findings point at built HTML; find the layout, partial, component or content file that produces it (Grep for the flagged text or tag). Prefer one change in a shared layout over the same change in many pages.

### 5. Plan and show the diff

Prepare all changes, then show them in one message, before any Edit or Write:

1. A table: file | check | what changes | expected points.
2. **One fenced `diff` block per file.** A table alone is not a diff. Use unified diff format with a few lines of context, for example:

   ```diff
   --- a/index.html
   +++ b/index.html
   @@ -3,4 +3,6 @@
      <meta charset="utf-8">
   -  <title>Home</title>
   +  <title>Visual bookmarks for research | InsightPins</title>
   +  <meta name="description" content="...">
   ```

3. For new files (llms.txt), the full content in a fenced block.

Then ask with AskUserQuestion (in a host without that tool, a plain question): **Apply all**, **Let me choose** (then ask per file or per check), or **Cancel**. With `--yes`, skip the question and apply, but only after the diffs are printed.

### 6. Apply

Use Edit for existing files (never rewrite a whole existing file with Write) and Write only for new files. Match the file's existing indentation and style. Apply only what the user approved.

### 7. Re-audit and report

Always re-audit; a fix run is not finished without the after score.

For generated sites, ask whether to rebuild before re-auditing (a re-audit without a rebuild reads the old output). Then:

```bash
node ${CLAUDE_PLUGIN_ROOT}/skills/audit/scripts/audit.mjs .
```

This rewrites `aeotester-report.md`. Report in chat:

- score before -> after as `total / available` with the percentage,
- what was fixed, per check,
- what was skipped and why,
- assisted items still open,
- a reminder that nothing was committed: review with `git diff`.
