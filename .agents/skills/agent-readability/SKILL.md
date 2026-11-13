---
name: agent-readability
description: Improve, validate, and publish AI-agent-readable websites using the Vercel Agent Readability Spec, llms.txt, Markdown mirrors, semantic HTML, accessibility checks, and source-to-deployment evidence.
---

# Agent Readability

Use this skill for Agent Ready scans, crawler-readability remediation, llms.txt and sitemap work, HTML/Markdown parity, static-site metadata, accessibility, and public-page publication verification.

## Operating sequence

1. Read the complete scan report and capture the scan ID, score, page count, check groups, and exact failing check IDs.
2. Rank work by discovery, extractability, metadata, accessibility, and publication impact.
3. Resolve each scanned URL to its canonical source file and deployment workflow.
4. Edit the owning source. Treat generated mirrors as publication artifacts.
5. Validate source files and Markdown mirrors with the repository contract.
6. Publish through the canonical workflow and capture its run ID and source SHA.
7. Fetch the deployed HTML and Markdown, then run a fresh Agent Ready scan.
8. Record score, scan ID, discovered/scanned page counts, llms.txt score, accessibility score, and remaining checks.

## P8 — Open Graph description

Every public HTML page carries a page-specific Open Graph description of at least 50 characters:

`<meta property="og:description" content="A useful page-specific summary of at least 50 characters">`

The description matches the page's purpose and complements its meta description. The source validator checks the populated content value.

## Page contract

Use the following fields on each public page where applicable:

- Canonical URL.
- Meta description of at least 50 characters.
- Open Graph title and description.
- Schema.org JSON-LD with type, name/headline, description, URL, and dateModified.
- HTML language, title, main landmark, skip link, and meaningful heading structure.
- Markdown alternate link with `type="text/markdown"`.
- llms.txt discovery link with `rel="describedby"`.
- AI snippet directives that match the site's indexing policy.
- Glossary navigation and source links.
- Static content that remains meaningful before JavaScript executes.

## Discovery contract

Publish root `llms.txt`, expanded `llms-full.txt`, `sitemap.xml`, and `sitemap.md`. Keep `AGENTS.md` useful to automated clients with Configuration and Usage sections, canonical origins, entry points, and authority boundaries.

## HTML and Markdown representations

- Keep canonical Markdown mirrors beside their HTML routes.
- Add YAML frontmatter with title, description, and last_updated.
- Preserve headings, links, lists, tables, code fences, and source references.
- Link Markdown mirrors to their canonical HTML destinations.
- Use static alternate links on GitHub Pages. Add content negotiation only on a host that supports programmable response headers or server routing.
- Treat HTML and Markdown as parallel projections of a shared content contract.

## Public text integrity

Public HTML, Markdown, llms.txt, sitemap files, and Agent Ready fixtures use directly readable text. Keep zero-width and bidirectional control characters out of these surfaces. Internal encoding experiments use separate files, a visible canonical sidecar, a documented decoder, and round-trip fixtures.

## MaxC boundary

The current MaxC implementation compiles MaxUp to HTML, Leptos, and MaxC bytecode. A reverse HTML-to-MaxUp module exists; current workspace CLI wiring remains incomplete. MaxC bytecode is serialized MaxUp AST. Markdown conversion remains a separate adapter capability; use the documented parallel design in `docs/ops/MAXC-INTEROP-STATUS.md`.

## Recognition badge

Show the public Agent Ready badge only when a verified scan receipt contains:

- `score >= 95`;
- a public scan URL;
- a verification timestamp.

Keep the badge hidden while the score is unknown or below threshold. Keep the displayed score bound to the receipt that earned it.

## Evidence discipline

Separate source validation, workflow execution, deployment verification, and live scan results. A passing source test proves the authored files satisfy the contract; a successful deployment run proves publication execution; a fresh scan proves the current public response.
