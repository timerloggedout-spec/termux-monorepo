---
description: "Ask the AnimatedWebs team for a template the library does not have, or check your earlier requests"
argument-hint: "[what you want built; leave empty to see your requests]"
---

If "$ARGUMENTS" is empty, call `manage_request` with action `list` and show each request with its id, date and status (received, reviewed or cancelled). Offer to cancel one that is still received with action `cancel`.

Otherwise search first: call `search_catalog` for "$ARGUMENTS" and show the closest matches. Only if none of them fits, send the brief with `request_template` (subject, industry, style and references, 10 to 1500 characters) and report the request id. Send it once: every call creates a new request.
