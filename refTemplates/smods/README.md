# sMods — governed custom-fork pins

This directory is the live, shallow custom-fork lane for references that have
passed the repository's selection and compatibility review.

## Canonical sources of truth

- `.gitmodules` declares each submodule's exact path and HTTPS source URL.
- The repository tree records the immutable gitlink commit SHA at each path.
- `scripts/ci/refTemplates_inventory.py --strict` enforces one-to-one parity.

Do not add a directory-shaped placeholder or a prose-only pin. A valid sMods
entry must have exactly one `.gitmodules` path and one mode-160000 gitlink.
The URL must be credential-free HTTPS on github.com, and the submodule must
declare `shallow = true`. The gitlink SHA, not the optional tracking branch,
is the revision actually consumed by a checkout.

## Operating rules

- Do not recursively initialize or fetch sMods in ordinary CI.
- Do not replace a pin with a floating branch reference.
- Update a pin only through a reviewed commit that changes the gitlink SHA.
- Keep credentials, browser profiles, cookies, local storage, and session
  exports outside this directory and outside Git.
- Keep metadata-first template records under their numbered category; use a
  reusable template before creating a new integration-specific structure.
- Every reusable template child requires nonempty `README.md` and
  `SOURCE.txt`; runtime integration templates additionally require
  `integration.json`.
