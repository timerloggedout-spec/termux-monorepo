---
name: page-patterns
description: Names one locked page pattern (list, detail, form, dashboard, settings, board, calendar, split pane, analytics, inbox) before any new page is built. Use when creating a screen, route, layout, dashboard, settings page, list, form page, inbox, calendar, board, or marketing landing.
title: Page Patterns
category: interaction
severity: hard-rule
references:
- reference/decision-tree.md
- reference/catalog.md
- reference/marketing.md
---

If `.ux-profile.md` exists at the project root, read it before choosing a layout.

### Intent

A page that mixes list, dashboard, and settings into one scroll is hard to use and harder to maintain. This skill forces a single named pattern **before any page markup**. Chrome, widgets, and empty states sit inside a pattern — they are not patterns themselves.

### Hard Rules (Non-Negotiable)

- **Name the pattern in chat before writing page markup.** No `<main>`, route file, or page component until the name is stated. If the surface is still undecided, run `surfaces` first (inline / slide-over / page). Only pages continue here.
- **Every new page is exactly one of the ten product patterns**, or a marketing composition from [reference/marketing.md](reference/marketing.md), or you stop and ask. Do not invent an eleventh product pattern.
- **App chrome is not a page.** Sidebars, headers, footers, and dropdowns frame pages. Do not treat a shell as the pattern.
- **Components sit inside a pattern.** Charts, KPI tiles, dialogs, file upload, and empty states never replace the page type.
- **View modes are not new pages.** List ↔ Board ↔ Calendar of the **same** records is one page with a toggle. Shared search and filters stay put.
- **Empty states keep the pattern’s skeleton.** A calendar still shows the grid. A list still shows the header, search, and a **visible** table frame (L1 surface + hairlines — not a bare DOM wrapper on L0). Do not swap the page for a blank illustration.
- **Catalog Must lines are hard rules.** For List / Index: the table sits in a visible L1 frame with hairlines; search is recognizable at a glance on medium/wide; clickable rows have a resting affordance; disabled pagination keeps readable labels. Restraint never drops that chrome.

See [reference/decision-tree.md](reference/decision-tree.md) to pick the pattern. See [reference/catalog.md](reference/catalog.md) only for the pattern you named.

### Design Heuristics & Taste Principles

- Ask “what is the user’s one job on this URL?” The answer is the pattern.
- Dashboard is a glance. Analytics is explore-and-filter. Do not mix them.
- Settings configure the product. Detail shows one record. Do not put record fields on Settings.
- Auth (login, register, forgot, reset, verify, 2FA) is **Form (auth)** — a centered card, no app sidebar.
- Public marketing pages are composed sections, not a product pattern. Name the route type (home, about, contact, …) then stack sections.
- Why (Laws of UX): People expect your screens to work like the ones they already know (Jakob’s Law, Jon Yablonski). Lock a familiar pattern before inventing a layout. https://lawsofux.com/jakobs-law/

### Concrete Scenarios (Before vs. After)

#### ❌ Anti-Pattern

The agent starts a “Projects home” with a sidebar, five KPI cards, a filterable table, inline settings toggles, and a calendar. No pattern is named. The empty state replaces the whole layout with a cartoon.

#### ✅ Best Practice

The agent writes: **Pattern 1 — List / Index.** Then it builds a heading, one-sentence description, search, one Filters control, a table, and pagination. Create opens a slide-over (`surfaces`). Settings is a separate route: **Pattern 5**. Empty state sits inside the table frame.

### Framework-Agnostic Implementation Blueprint

```
if task is inline edit or slide-over:
  stop — use surfaces; this skill is for pages only

pattern = decide(userJob)   // decision-tree.md — exactly one name
state the pattern in chat
read catalog.md for that pattern only
then write markup that matches the named anatomy
```

**The ten product patterns**

| # | Name | User’s job |
| --- | --- | --- |
| 1 | List / Index | Scan and manage many records |
| 2 | Detail / Record | Inspect one record |
| 3 | Form | Enter or edit data |
| 4 | Dashboard / Overview | Glance at status; no drill |
| 5 | Settings / Configuration | Configure the product |
| 6 | Kanban / Board | Move items through stages |
| 7 | Calendar | Work by date and time |
| 8 | Split Pane | Triage many items without leaving |
| 9 | Analytics / Reporting | Filter, drill, export data |
| 10 | Inbox / Activity Feed | Work a time-ordered queue |

**Does not map? Stop.** Infinite canvases, node graphs, AI chat as the page, and command palettes as IA are not patterns. Ask before building.

Width-cap and center **main page content** (`main`, `.page`) so it does not hug the sidebar or stretch edge-to-edge. Do not cap the app shell or chrome (`viewports`). Use the project’s spacing tokens (`spacing`). On narrow viewports follow `viewports` and this catalog’s **Narrow** line.

### Agent Checklist

- [ ] Read `.ux-profile.md` if present.
- [ ] Confirm this is a **page** (not inline, slide-over, chrome, or a widget).
- [ ] Walk [reference/decision-tree.md](reference/decision-tree.md) and **state the pattern name** (or marketing route type) in chat.
- [ ] Read only that pattern in [reference/catalog.md](reference/catalog.md) (or [reference/marketing.md](reference/marketing.md)).
- [ ] Build the named anatomy — do not add KPI strips to lists, filters to dashboards, or DataTable chrome to inboxes.
- [ ] Empty, loading, and error states stay inside the pattern frame (visible L1 + hairlines for lists — not bare L0).
- [ ] List / Index: search recognizable on medium/wide; rows have resting affordance; disabled pagination stays labeled.
- [ ] Apply that pattern’s **Narrow** line; chrome collapse is `viewports`.
- [ ] After build: a reviewer can name the same pattern from the layout alone.
