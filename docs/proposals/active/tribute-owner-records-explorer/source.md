# Source brief — Tribute Owner Records Explorer

Origin: direct user instruction to finish the in-flight Owner Records Explorer implementation, with scope established by PR #5448 and its reviewed implementation.

The implementation is intentionally metadata-only. It exposes searchable/filterable L1 metadata from the validated `owner-records/v1` envelope and does not fetch ciphertext bodies, request age identities, or decrypt. GitHub Pages remains a public metadata projection. Vercel SSO and XML staging are access-control/transport measures, not proof of browser decryption.

The Admin + Tracking discovery boundary (D4) is a product contract. The deployment build must preserve it: `versioning.js` loads shared primary navigation and an all-pages version menu, so the build manifest generator must not inject that script into `owner-records.html`. The page verifies its own same-origin `version-manifest.json` and can therefore retain build identity without the shared script.

Browser-side age decryption is a separate blocked item pending a threat model, browser-compatible implementation, zero-network plaintext handling, and independent security review.
