# Research: Gemini Interactions API

## Context
Hindsight's `GeminiLLM` adapter calls the `generateContent` surface via
`google.genai`. Google's deprecation notice for `gemini-2.0-flash`
recommended migrating to `gemini-3.8-flash` via the "Interactions API".
Hindsight 0.10.2 does not speak that surface — fact extraction returns
HTTP 500 with no traceback.

## Questions
1. What is the Interactions API surface? Endpoint shape, auth, request/response.
2. Which Gemini models require it vs. accept `generateContent`?
3. Does `google.genai` (new SDK) route to it transparently, or is it a
   distinct client?
4. Is there a compatibility shim for `generateContent` on 3.8+ models?
5. What's the retirement timeline? Do 3.5/3.6 remain available?
6. Pricing/quota differences between surfaces on free tier.

## Deliverable
`docs/STANDARDS/RESEARCH/gemini-interactions-api.md`
- Summary
- Endpoint diff table
- Model → surface matrix
- Shim availability
- Recommendation for Hindsight 0.10.2 + future 0.11+

## Acceptance
- Every claim sourced (Google docs, changelog, or SDK code).
- Explicit `NEED_EVIDENCE` tags where uncertain.
- One-paragraph recommendation for our `HINDSIGHT_API_LLM_*` config.

## Lane
Observatory · research · dispatch queue
Priority: medium (Hindsight runs on 3.5-flash; unblock when Google retires 3.5)
