# Venue-execution machinery (QUE #5254)

Owner directive 2026-11-12: venue-requirement legs (demo/media
upload → public URL → filing) run in GitHub Actions machinery, not
seat-browser legs. The D3 Clips upload (seat-browser, stamped
DEVIATION on #5137) is the instance this supersedes.

## Shape

- **Census-driven.** The executor (`scripts/venues/venue_execution.py`)
  reads the entry's `submission-requirements.json` (classes from the
  #5096 census) and its `venue-execution.json` bindings
  (requirement → adapter + venue params + filing issue). Only
  `fleet-executable`, non-discharged requirements with a binding
  execute; everything else skips with a named reason.
- **Legs per requirement:** adapter execute → unauthenticated
  verify of the public artifact (a fresh request with NO credential
  headers — a login-walled URL fails this leg by construction) →
  receipt stamp on the entry's filing (venue + URL + verify
  evidence).
- **SUBMIT-ONCE in machinery.** State keyed
  `{slug}/{venue}/{requirement}` in `ops/venue-execution/state.json`
  (committed by the workflow). A verified execution is read back on
  later fires — the adapter is never re-invoked for a submit-once
  requirement; the recorded URL is re-verified instead.
- **Fail-visible.** Venue refusal/closed state = named receipt
  (e.g. `venue_auth_missing`, `venue_http_403`) and a failed run —
  never a silent seat fallback. A seat-browser leg remains a
  stamped deviation, never the default route.
- **Credentials** are fleet venue accounts via sealed secrets,
  named in bindings by env var name of record only.

## Adapters (v1)

- **webform** (`scripts/venues/webform_adapter.py`) — form-only
  venues: configurable multipart POST from the binding
  ({endpoint, fields, file_field, url_extract}); a new form venue
  is a binding, not code.
- **clips** (`scripts/venues/clips_adapter.py`) — agent-native
  Clips. Established firsthand: the public agent API
  (agent-context/transcript/frames) is read-only and powers the
  verify/read leg for existing clips; upload sits behind the
  fleet-account authenticated surface (MCP connect) — no
  unauthenticated upload endpoint exists. The upload leg requires
  the sealed fleet credential (`CLIPS_FLEET_TOKEN`, name of
  record); absent it, the adapter returns the named refusal
  `venue_auth_missing`.

## Live proof

Entry `entries/venue-machinery-proof/` (machinery fixture, not a
competition entry) binds its `proof-upload` requirement to the
webform adapter. The venue-execution workflow's run on it —
upload → public URL → unauthenticated verify → receipt on #5254 —
is the filing's done-evidence ②, stamped on the filing as it lands.
