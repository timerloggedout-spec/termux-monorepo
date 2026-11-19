---
name: verbs
description: Enforces verb-first CTA and button labels; bans OK, Submit, and Proceed. Use when writing buttons, links, menus, or reviewing UI microcopy.
title: Verbs
category: voice
severity: hard-rule
references:
- reference/verb-dictionary.md
---

If `.ux-profile.md` exists at the project root, read it first — especially **Brand tone and microcopy voice** and capitalization settings.

### Intent

Action labels are navigation, not decoration. Every button, link, and menu item tells the user exactly what will happen when they activate it. Verb-first copy removes guesswork, shortens decision time, and keeps the interface scannable.

### Hard Rules (Non-Negotiable)

- **Every CTA, button, and action link starts with a strong imperative verb.** Examples: Export CSV, Create project, Connect repository, Delete workspace, Save changes.
- **Ban ambiguous labels:** OK, Submit, Proceed, Continue — unless the control is the explicit next step in a multi-step sequential wizard where the destination step is already visible in the wizard chrome.
- **Uniform capitalization:** Sentence case for UI copy and buttons (e.g., Save changes, not Save Changes or SAVE CHANGES). Match whatever `.ux-profile.md` specifies if it differs.

### Design Heuristics & Taste Principles

- Prefer **verb + object** over verb alone when the object disambiguates: Export CSV beats Export; Delete workspace beats Delete.
- Keep labels short: 1–3 words when possible. Longer only when the object name is required for safety (Delete workspace "Analytics").
- Destructive actions still lead with the verb but name the entity: Delete project, Remove member — never Are you sure? on the button itself.
- Secondary actions use equally specific verbs: Cancel, Discard changes, Go back — not Dismiss or Close when the user is abandoning work.
- Menu items follow the same rule: View details, Edit settings, Copy link — not Details or Settings alone when those could mean navigate vs. open vs. expand.

See [reference/verb-dictionary.md](reference/verb-dictionary.md) for Save vs Create vs Publish pairings and action-object syntax.

### Concrete Scenarios (Before vs. After)

#### ❌ Anti-Pattern

A form footer has two buttons: Cancel and Submit. A modal footer has OK and Cancel. A settings page link reads Continue to billing. A toolbar button says Proceed after a file upload completes.

#### ✅ Best Practice

The form footer shows Cancel and Save changes (or Create account on first save). The modal confirms with Delete workspace and Cancel. Settings link reads View billing. Post-upload button reads Import 24 contacts.

### Framework-Agnostic Implementation Blueprint

```html
<!-- Primary action: verb + object -->
<button type="submit">Save changes</button>

<!-- Destructive: verb + named entity -->
<button type="button" data-action="delete">Delete workspace</button>

<!-- Link styled as action -->
<a href="/projects/new">Create project</a>
```

Audit pass: collect all `<button>`, `[role="button"]`, and action `<a>` nodes; flag any label that does not start with an approved imperative verb or appears on the ban list.

### Agent Checklist

- [ ] Read `.ux-profile.md` if present (voice and capitalization).
- [ ] List every CTA, button, and action link in scope.
- [ ] Verify each label starts with a strong imperative verb.
- [ ] Remove or replace OK, Submit, Proceed, Continue (except allowed wizard steps).
- [ ] Confirm sentence case (or profile override) is consistent across the surface.
- [ ] Cross-check ambiguous verbs against [reference/verb-dictionary.md](reference/verb-dictionary.md).
