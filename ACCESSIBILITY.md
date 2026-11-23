# Accessibility

Accessibility is part of the monorepo's engineering and review process. Changes to interfaces, documentation, command-line flows, generated reports, and agent-facing outputs should consider the people who use them, including keyboard and assistive-technology users.

## How this repository applies accessibility

The pinned [Accessibility Agents integration](docs/accessibility/INTEGRATION.md) provides specialist routing, structured findings, and scanner guidance. The source fork is tracked at `refTemplates/smods/accessibility-agents_fork`.

For a change, select the relevant router and smallest adequate specialist set. Record the scope, criteria, locations, severity, remediation, and verification evidence. Distinguish automated scanner results from manual keyboard, screen-reader, cognitive, and document checks.

## Review expectations

- Prefer semantic structure and native controls.
- Preserve keyboard access, visible focus, meaningful labels, and logical reading order.
- Provide useful alternative text and descriptive link names.
- Check contrast and avoid communicating meaning through color alone.
- Make dynamic status and error feedback perceivable.
- Keep Markdown headings, tables, links, and code examples readable.
- Validate generated reports and agent outputs as user-facing interfaces.

## Improvement, not certification

The Open Source Accessibility Framework is used as a continuous-improvement reference. Action status requires evidence against the action's definition of done. A tool installation, workflow, scan, or self-assessment does not establish certification or complete conformance.
