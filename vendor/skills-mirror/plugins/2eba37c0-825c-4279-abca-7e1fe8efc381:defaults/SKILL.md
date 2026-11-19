---
name: defaults
description: Intelligent defaults and draft persistence so users avoid blank busywork. Use when designing forms, dropdowns, preferences, or saving draft state across routes.
title: Defaults
category: interaction
severity: hard-rule
references:
- reference/state-persistence.md
---

If `.ux-profile.md` exists at the project root, read it before changing surfaces, forms, or focus behavior.

### Intent

Blank forms and empty dropdowns force users to do work the system already knows how to do. Smart defaults and draft persistence remove repetitive choices and protect against accidental data loss from navigation or tab closure.

### Hard Rules (Non-Negotiable)

- **Never present a blank dropdown when a default can be inferred** from user timezone, locale, previous selection in session, or last-used value in local storage. Pre-select the best guess; user can change explicitly.
- **Form drafts auto-persist to local memory** (localStorage, IndexedDB, or session-scoped store). Accidental navigation, refresh, or tab close must result in **zero data loss** for in-progress forms — restore on return.

See [reference/state-persistence.md](reference/state-persistence.md) for draft auto-save heuristics and cache invalidation.

### Design Heuristics & Taste Principles

- Show inferred defaults as selected values, not hidden pre-fill — user must see what will submit.
- "Remember my choice" applies only to non-sensitive preferences; never persist passwords or payment details in localStorage.
- On restore, highlight restored draft subtly: "Draft restored — last edited 2 min ago" with Discard option.
- Defaults rank: explicit user preference > last used in this workspace > locale/timezone heuristic > safe system fallback.
- Clear persisted draft on successful submit or explicit Discard.
- Why (Laws of UX): Some complexity cannot be deleted — we absorb it so the user does not (Tesler’s Law, Jon Yablonski). Defaults and drafts do that work. https://lawsofux.com/teslers-law/

### Concrete Scenarios (Before vs. After)

#### ❌ Anti-Pattern

Timezone dropdown opens with "Select timezone…" and 400 options, no pre-selection. User fills a long compose form, clicks a help link, returns — form is empty. Country defaults to US for all users regardless of locale.

#### ✅ Best Practice

Timezone pre-selected from `Intl.DateTimeFormat().resolvedOptions().timeZone`, grouped with recent choices at top. Compose form autosaves every 2s to `localStorage`; returning user sees restored body and subject with discard link. Country defaults from browser locale with visible selected value.

### Framework-Agnostic Implementation Blueprint

```
function inferDefault(field):
  if userPreference[field]: return userPreference[field]
  if lastUsed[field] in localStore: return lastUsed[field]
  if field == "timezone": return Intl timezone
  if field == "locale" or "country": return navigator.language / region
  if field == "dateFormat": return locale default
  return null   // only then show neutral placeholder

function draftKey(formId): return `draft:${formId}:${userId || 'anon'}`

on input debounced 500–2000ms:
  serialize form → localStore.set(draftKey, { data, updatedAt })

on mount:
  if draft = localStore.get(draftKey): hydrate form, show restore banner

on successful submit or Discard:
  localStore.remove(draftKey)
```

Dropdown with inference:

```html
<select name="timezone" aria-label="Timezone">
  <option value="Australia/Sydney" selected>Sydney (GMT+11)</option>
  <!-- other options -->
</select>
```

Never use empty first option when a valid default exists.

### Agent Checklist

- [ ] Read `.ux-profile.md` if present.
- [ ] Audit dropdowns and selects: every one has inferred or remembered default unless truly unknowable.
- [ ] Implement draft auto-save for multi-field or long forms.
- [ ] Restore draft on return; offer Discard; clear on submit.
- [ ] Follow cache invalidation rules in reference doc.
- [ ] Do not persist sensitive fields locally.
