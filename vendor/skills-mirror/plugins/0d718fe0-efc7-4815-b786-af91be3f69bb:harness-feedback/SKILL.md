---
name: harness-feedback
description: "Run a kaizen retrospective on an agentic-harness run and, with the user's consent, file tool-improvement feedback as a GitHub issue on the upstream agentic-harness repo. Use after a harness-setup or harness-review run, or on its own in a postmortem / kaizen quality loop, whenever the user wants to give feedback, suggest an improvement, report friction or a bug, or 'open an issue to improve the tool'. It gathers what was done and the choices made during the run into the standard feedback format, redacts project-identifying details, and creates the issue only after explicit approval. Boundary: this files feedback about the agentic-harness TOOL upstream — it is not harness-review (which assesses THIS project's own harness and writes a review context), and not tracker-advisor or issue triage in the user's own project."
model: inherit
---

# Harness feedback — close the kaizen loop to the tool

A harness run teaches you something about the *tool* that built it — where it was clear, where
it dragged, what was missing. This skill captures that as structured, privacy-safe feedback and
files it as a GitHub issue on the **upstream `agentic-harness` repository**, so the tool improves
run over run. It is the outward-facing half of the feedback loop: `harness-setup` Step 7 routes
in-project feedback into the project's own files; this skill routes *tool* feedback upstream.

The standard format, the mandatory sections, the redaction policy, and the target repo are all
defined once in `${CLAUDE_PLUGIN_ROOT}/shared/feedback-format.md`. Read it before drafting —
everything below operationalizes it.

## This skill vs harness-review

`harness-review` assesses **this project's** harness and emits a review context for `harness-setup`
to act on locally. `harness-feedback` looks the other way: it sends feedback about the
**agentic-harness tool itself** to its public repo. "Review my harness" / "is the harness used
well" is `harness-review`. "Give feedback on the tool" / "this step of the plugin was confusing" /
"open an issue to improve it" / a kaizen retrospective on the run is this skill. Neither authors or
triages issues in the user's own tracker — that is the project's tracker, not this.

## When it runs

- **Right after a run** — `harness-setup` Step 7 and `harness-review`'s output both *offer* this
  skill. The run's context is still in the conversation, so the draft can be specific.
- **Standalone, in a kaizen loop** — invoked later (or via the `/feedback` command) as a
  postmortem. The run's context is gone, so Step 0 reconstructs it.

Either way the flow is the same; only where the facts come from differs.

## Step 0: Establish the context

Decide which entry you are in and gather the raw material for the draft:

1. **Fresh run** (this conversation just ran `harness-setup`/`harness-review`): pull the facts from
   the conversation — which skill ran, the architecture pattern and execution mode chosen, the
   Step 2b manifest, tools accepted or rejected, any SDD/tracker coordination, what the user
   amended.
2. **Standalone / later**: reconstruct from durable sources — the `CLAUDE.md` change-history table
   (it records `Date | Change | Target | Reason`), the `.claude/` inventory, and the user. Ask for
   anything you cannot ground in a source; do not invent specifics.

Read the user's intent: a quick suggestion, a friction report, or a bug. That becomes `Type`.

## Step 1: Run the retrospective

Walk the kaizen questions, mapping each onto a section of the standard format:

- What was done, and how did it turn out? → `What was done`
- Which choices did you make, and were the options clear? → `Choices made`
- What did you expect to happen? → `Expected outcome`
- What actually happened, and where did it drag or break? → `What happened / friction`
- What single change would have helped most? → `Suggested improvement`

Keep it short and concrete. One real friction point well described beats a vague wishlist. If the
user has nothing to add, say so and stop — never manufacture feedback to fill the form.

## Step 2: Draft in the standard format

Fill the body skeleton from `${CLAUDE_PLUGIN_ROOT}/shared/feedback-format.md`. Set `Type` to one of
`bug | friction | enhancement | docs | question`, and name the `Affected area` (skill / step /
agent / orchestrator) when you can — it routes the issue to the right part of the tool.

Collect `Environment` automatically, then redact it (Step 3):

```bash
jq -r '.version' "${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json"   # plugin version
claude --version                                                       # Claude Code version
uname -sr                                                              # OS
```

## Step 3: Redact before anything leaves the machine

The issue lands on a **public** repo. Apply the redaction policy in
`${CLAUDE_PLUGIN_ROOT}/shared/feedback-format.md`: strip repo/org and product names, absolute paths
(→ `<path>`), proprietary domain terms, secrets, internal URLs, and people's names; keep the generic
stack and the harness mechanics. This is your job, not the user's — do it by default, then let the
user confirm the redacted text in Step 5. When unsure whether a detail is identifying, generalize it.

## Step 4: Completeness gate

The upstream CI check rejects an issue that is missing any mandatory section, so check it here first.
Confirm all eight mandatory sections — `Summary`, `Type`, `What was done`, `Choices made`,
`Expected outcome`, `What happened / friction`, `Suggested improvement`, `Environment` — hold real
content (not an empty hint, `_No response_`, or `TODO`). If any is thin, ask the user to fill it
before publishing. Filling it now means the issue passes the bot on the first try.

## Step 5: Consent, then publish

Show the **exact** issue body and the title (`[feedback] {summary}`) and ask for explicit approval.
Creating a public issue is an outward-facing, hard-to-undo action — never file without a clear yes.

On approval, write the body to a temp file and create the issue against the upstream repo. Keep the
`[feedback]` title prefix — the CI bot keys on it and applies the `feedback` label itself, so a
reporter who cannot set labels (a non-collaborator) is still routed. Labelling is best-effort: try
with the label, and fall back to creating without it if that is rejected.

```bash
gh issue create \
  --repo MrBogomips/agentic-harness \
  --title "[feedback] {summary}" \
  --label feedback \
  --body-file "{tmpfile}" \
  || gh issue create \
       --repo MrBogomips/agentic-harness \
       --title "[feedback] {summary}" \
       --body-file "{tmpfile}"
```

**Preflight `gh`.** Only use `gh` if it is present and authenticated — check with `command -v gh`
and `gh auth status`. If either fails, **fall back** to a prefilled browser URL instead of erroring:
build a new-issue link with the label and the URL-encoded title and body, and give it to the user to
open. (`labels=feedback` applies the label; passing `body=` prefills the drafted text — do not also
pass `template=`, which would override the body.)

```bash
# URL-encode title and body, then assemble:
# https://github.com/MrBogomips/agentic-harness/issues/new?labels=feedback&title=<enc>&body=<enc>
title_enc=$(printf '%s' "[feedback] {summary}" | jq -sRr @uri)
body_enc=$(jq -sRr @uri < "{tmpfile}")
echo "https://github.com/MrBogomips/agentic-harness/issues/new?labels=feedback&title=${title_enc}&body=${body_enc}"
```

Report the created issue's URL (or the prefilled link) back to the user.

## Step 6: Record it (standalone path)

When run standalone against an existing harness, append a row to the `CLAUDE.md` change-history
table noting that feedback was filed and the issue link, so the same item is not re-filed in a later
kaizen pass. (After a fresh run, the conversation already carries this — no extra record needed.)
Recording history is a write; if `harness-review`'s read-only contract is in force in the current
context, leave the note as a recommendation for `harness-setup` instead of writing it yourself.

## Checklist

- [ ] `Type` is one of the allowed values; `Affected area` named where known.
- [ ] Project-identifying details redacted per the policy; only tool-improvement signal remains.
- [ ] All eight mandatory sections hold real content (completeness gate passed).
- [ ] The exact body and title were shown and **explicitly approved** before publishing.
- [ ] `gh` was preflighted; the browser-URL fallback was used when `gh` was unavailable.
- [ ] The created issue / prefilled link was reported back to the user.

## References

- `${CLAUDE_PLUGIN_ROOT}/shared/feedback-format.md` — the canonical format: fields and provenance,
  the mandatory-section list, the redaction policy, the upstream repo slug, and the fill-ready body
  skeleton.
