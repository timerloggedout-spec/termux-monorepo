---
name: forms
description: Blur-first validation, instant error clear, fewer fields, clickable submit. Use when building forms, inputs, wizards, or fixing validation UX.
title: Forms
category: interaction
severity: hard-rule
references:
- reference/form-best-practices.md
---

If `.ux-profile.md` exists at the project root, read it before changing surfaces, forms, or focus behavior.

If this form is a dedicated page (auth, wizard, or long edit), name **Pattern 3 — Form** via `page-patterns` before writing the page.

### Intent

Forms punish users when errors appear too early, linger too long, or block submission with a dead button. Validation should reward correction, reduce field count, and never trap the user behind a disabled submit control.

### Hard Rules (Non-Negotiable)

- **Never mark invalid while typing in a pristine field.** No red borders, error text, or `aria-invalid="true"` until the field has been blurred at least once without a valid value.
- **Trigger validation on initial blur.** First leave-event runs full field rules; empty required fields error on blur, not on first keystroke.
- **Once invalid, clear error immediately on focus or first corrective keystroke.** Do not wait for re-blur to remove error styling after the user engages with the field.
- **Eliminate redundant fields.** Infer city/state from postal code; use single Full Name unless legally required to split; merge related optional fields into one where possible.
- **Disabled submit buttons are prohibited.** Keep submit clickable at all times; on click with incomplete/invalid data, scroll to first error and show inline messages — never a silent no-op.

See [reference/form-best-practices.md](reference/form-best-practices.md) for keyboard submit, autocomplete attributes, input masking, and field reduction patterns.

### Design Heuristics & Taste Principles

- Show helper text before error text occupies the same slot — errors replace helpers, not stack below labels.
- One error message per field; lead with the fix ("Enter an email like name@domain.com"), not the failure ("Invalid email").
- Group related fields; validate optional fields only on blur if touched.
- Submit shows inline loading on the button, not a page freeze; preserve entered values on server error.
- Required fields: visible label + `required` attribute; do not rely on placeholder or color alone.
- Why (Laws of UX): More choices slow the decision (Hick’s Law, Jon Yablonski). That is why we cut fields and keep one path. https://lawsofux.com/hicks-law/

### Concrete Scenarios (Before vs. After)

#### ❌ Anti-Pattern

Email field turns red while typing "j" in an empty form. Submit button stays `disabled` until all fields pass — user clicks nothing happens with no feedback. Form asks First Name, Last Name, City, State, ZIP when ZIP lookup can fill city/state. Error clears only after blur even though user deleted the bad character.

#### ✅ Best Practice

User types partial email — no error until tab-out. On blur with "j@", inline error appears. User focuses field — error clears immediately; first keystroke keeps field neutral. Submit always enabled; click with missing ZIP scrolls to ZIP and shows "Enter a postal code." Single Full Name field; ZIP autofill populates read-only city/state.

### Framework-Agnostic Implementation Blueprint

```
state per field: pristine | touched | valid | invalid

on blur(field):
  field.touched = true
  validate(field)
  if fail: field.state = invalid, show message
  else: field.state = valid

on focus(field):
  if field.state == invalid:
    hide message, remove aria-invalid (keep touched)

on input(field):
  if field.state == invalid:
    clear error on first keystroke
  if field.touched:
    validate(field)   // optional live validate after first blur

on submit click:
  touch all fields
  if any invalid: prevent submit, focus first invalid, scroll into view
  else: submit
```

```html
<label for="email">Email</label>
<input id="email" name="email" type="email" autocomplete="email"
       aria-describedby="email-error" />
<p id="email-error" role="alert" hidden>Enter an email like name@domain.com</p>
<button type="submit">Save changes</button>  <!-- never disabled -->
```

### Agent Checklist

- [ ] Read `.ux-profile.md` if present.
- [ ] If this is a form page (not a slide-over), name Pattern 3 via `page-patterns` first.
- [ ] Confirm pristine fields never show validation errors during typing.
- [ ] Validation fires on first blur; errors clear on focus or first corrective keystroke.
- [ ] Audit field list for redundancy; remove or infer where possible.
- [ ] Submit button is always clickable; click surfaces inline errors when incomplete.
- [ ] Apply autocomplete attributes and patterns from reference doc.
