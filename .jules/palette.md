## 2026-08-25 - Lit-HTML Async Button Accessibility and States
**Learning:** In lit-html reactive component closures, async button clicks without `aria-busy` and `?disabled` boolean attribute bindings allow duplicate triggers and fail to inform screen readers of in-progress operations.
**Action:** Always bind `aria-busy=${isProcessing ? 'true' : 'false'}` and `?disabled=${isProcessing}` to async trigger buttons, updating button text during pending states.
