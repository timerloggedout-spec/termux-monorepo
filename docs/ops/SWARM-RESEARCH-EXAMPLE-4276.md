# SWARM RESEARCH — worked example #2: issue #4276, WebView state-fetch under a file:// origin (2026-11-03)

Second worked example for SWARM-RESEARCH-TEMPLATE.md (example #1:
the #4283 AVD case). Research item: issue #4443, owner order
2026-11-03. Producer: optimizations-assurance (Swarm seat-build),
claim 6608934980. The fix under research had ALREADY landed on the
engineering call when this run started — the template's job here
is the verdict discipline: does the outside record + our own
evidence corroborate the landed fix, contradict it, or leave it
incomplete?

## Preflight — leg states

- **SOFA (primary): LIVE.** Agent `Inquest`
  (a1bac8d7-d467-4c00-a04b-1501fa60beaf), contributor,
  publish_directly, all 10 scopes verified by `sofa.py status`
  this run (the agent was renamed in place from its creation
  name; id unchanged).
- **Cross-check leg: LIVE.** Gate artifacts downloadable
  in-process; the owner device recordings are in-tree at
  `apps/studysprint/evidence/apk/` (PR #4427).
- **Local leg: N/A** — no reproduction needed; the fleet record
  (attempts 1–3) is the reproduction corpus.

## 1. Intake

**Problem.** The StudySprint APK's bundled web app fetches
`data/state.json` at boot. Inside the WebView the fetch fails —
the page origin is `file://`. On the owner device the failure
held for 0.1.0 (bare file-origin) AND for 0.1.1
(`shouldInterceptRequest` serving the bundle's own assets with
`Access-Control-Allow-Origin: *`). In the AOSP emulator's older
WebView (gate attempt 2, run 41657475081) the same bundle
rendered the named load-failure state ("Couldn't load your
course data"). The identical bundle renders fine in Chrome.

**Already eliminated firsthand (attempt 2, do not re-derive):**
state.json missing (build.sh's own final guard fails the build
unless `assets/web/data/state.json` is in the APK; build step
green) · interceptor absent (present on master, ACAO:*) ·
harness fault (repro run 41657458297 fired with the exact #4276
signature).

**Landed fix (the claim under research).** PR #4423 merged
4b9b8c76c72a, surfaces 0.1.3: the bundle loads from
`https://appassets.androidplatform.net/assets/web/index.html`
and a `shouldInterceptRequest` handler serves that reserved
domain's `/assets/` tree from the APK assets — page and fetch
share ONE secure https origin. Framework APIs only (the build
is SDK-direct; androidx.webkit is not in android.jar) — stated
on the claim and the PR, not buried.

**Kill-or-prove, stated in advance of the verdict (bound by the
issue):** the appassets claim DIES if (a) the attempt-3 green run
still fails the state fetch under the https origin, or (b) the
owner's 0.1.3 device smoke fails the same way the 0.1.1 smoke
did. It is PROVEN (for the populations tested) if attempt 3
renders state in the emulator's older WebView AND the device
smoke renders on modern hardware WebView.

## 2. Atoms

1. **file-origin fetch blocking** — fetch/XHR from a `file://`
   page origin (null/opaque origin) blocked in WebView despite
   same-directory relative URLs.
2. **interception + CORS limits** — what
   `shouldInterceptRequest` + `Access-Control-Allow-Origin: *`
   can and cannot cure for a file-origin page.
3. **the canonical pattern** — WebViewAssetLoader /
   `appassets.androidplatform.net`: the documented route for
   serving app assets over an https origin, and the fidelity of
   a framework-only equivalent (same reserved domain, same
   interception point).
4. **WebView generation divergence** — older AOSP WebView vs
   modern WebView behavior on intercepted file-origin requests.

## 3. SOFA search (per atom; full-read before ranking)

Searches run this session via the connector helper
(`sofa_search`); two candidates full-read via `sofa_get_post`.

- **Atom 1** — "fetch file origin blocked WebView" · "XHR file
  origin CORS null origin WebView". Hits: a Delphi/TMS
  Google-Maps API-key question (621beeca, trust: not enough
  evidence) and a WKWebView (iOS) origin TIL (6c70b6b5, +15,
  verified 2026-10-10). Neither is about Android WebView
  file-origin fetch. **Miss.**
- **Atom 2** — "shouldInterceptRequest
  Access-Control-Allow-Origin". Hits: two Delphi TWebHttpRequest
  CORS-preflight questions (05d869e2, ca393762; both trust: not
  enough evidence) — a desktop framework's HTTP component, not
  Android interception. **Miss at the atom's terms** — but see
  the adjacent hit under atom 4.
- **Atom 3** — "WebViewAssetLoader appassets" ·
  "appassets.androidplatform.net" · "webviewassetloader". Hits:
  a Delphi WebView2 local-images question (127d5e86), a TMS
  blank-screen question (5f65d08c), a WebView2Loader question
  (57ce18ab), and an App Links TIL (d72d58b5, +33, verified
  2026-10-07) — full-read: it is about assetlinks.json domain
  verification for deep links, a different mechanism that shares
  only the string "appassets". A playbook-flavored search
  ("android webview local assets playbook") surfaced no
  playbook. **Miss — total: SOFA carries no WebViewAssetLoader
  content at all.**
- **Atom 4** — "AOSP WebView intercepted request older version
  divergence". One mechanically adjacent hit, full-read:
  question 5f300ae5, "How should an Android WebView enforce a
  host allowlist for subresources without breaking embedded
  content?" (yunghermes, 2026-08-17; answer trust: not enough
  evidence; its reply's claims all `untested`). The reply
  documents real interception limits — interception observes
  only the initial URL of a redirect chain, never receives
  javascript:/blob: URLs, must stay background-safe. True and
  useful platform knowledge, adjacent to atom 2's mechanics —
  but it says nothing about file-origin fetch, CORS on
  intercepted responses, or generation divergence. **Adjacent,
  ranked below the fleet record; not evidence for the verdict.**

**SOFA yield: ∅ applicable evidence on all four atoms.** The
adjacent 5f300ae5 is recorded for what it is (unverified,
adjacent). No result was ranked without a full read.

## 4. Cross-check vs our own record (the carrying leg)

The fleet record answers every atom firsthand; where it speaks,
it outranks SOFA per the template.

- **Atom 1 — ANSWERED by the record.** Attempt 1/2 repro runs
  (41657458297 line) + the owner 0.1.0/0.1.1 device recordings
  (evidence/apk, incl. recording 073809's persistent "Loading
  your course…") establish the failure on both populations.
- **Atom 2 — ANSWERED by the record, in the negative.** 0.1.1
  carried interception + ACAO:* and still failed on the device
  AND the emulator. Whatever the theory of intercepted CORS,
  the empirical bound is: interception from a file origin does
  not cure the fetch in either WebView population we run. (The
  SOFA-adjacent 5f300ae5 limits point the same direction —
  interception is a partial surface — but the verdict does not
  need it.)
- **Atom 3 — ANSWERED by attempt 3.** Green run 41668222509,
  artifact 13245813913: the bundle renders FULLY from the https
  origin in the AOSP emulator's older WebView — Today populated
  from state ("Today (day 1): 2 session(s). First up: learn —
  cell structure (45 min)"), footer version 0.1.3 present. The
  framework-only equivalent behaved identically to the pattern
  it implements (same reserved domain, same interception
  point). The run's stamped FAIL was a harness assertion defect
  (uiautomator splits the footer into sibling text nodes; the
  line-wise version regex could never match) — fixed in PR
  #4444 (joined-text assertions), NOT an app failure; recorded
  in full on #4283 (comment 6608907286).
- **Atom 4 — PARTIALLY ANSWERED.** Divergence is real inside
  our record (modern Chrome renders the file-origin bundle; the
  older emulator WebView does not; the device WebView matched
  the emulator, not Chrome). Under the https origin the
  emulator population renders — the divergence is routed around
  rather than characterized per-version. No per-version matrix
  exists in our record or in SOFA's.

## 5. Verdict — ONE, on the landed fix

**INCOMPLETE** — corroborated on the emulator leg, deciding leg
still open.

- Attempt 3 satisfies kill-or-prove clause (a) in the fix's
  favor: the state fetch lands under the https origin in the
  exact WebView population that defeated both prior builds. The
  claim "page + fetch on one secure https origin cures the
  load" is **corroborated** for the emulator population.
- Clause (b) is unrun: the owner's 0.1.3 device smoke (build of
  record: run 41668240689, artifact 13245909653) has not
  happened. Until it renders on the device, the verdict cannot
  rise to corroborated outright — #4276's acceptance split of
  record keeps the device smoke as the closer, and this
  research does not pre-empt it.
- What flips it: device smoke renders state + footer 0.1.3 ⇒
  **corroborated** (both bound legs). Device smoke reproduces
  the loading hang ⇒ **contradicted**, the appassets claim dies,
  and the next research cycle opens on the device WebView's
  behavior specifically (the one population no leg here could
  interrogate).

Provenance: this verdict rests on the fleet record (runs
41657458297 · 41657475081 · 41668205988 · 41668222509 ·
41668240689 and their artifacts; evidence/apk recordings). SOFA
contributed no applicable evidence — recorded as a clean miss,
not silently skipped.

## 6. ASK draft (total miss on atom 3 — drafted, NOT posted)

Per the template, a total miss drafts an ASK; posting is a
separate gate. The draft:

> **Serving bundled web assets in Android WebView: is a
> framework-only shouldInterceptRequest handler for
> appassets.androidplatform.net equivalent to
> androidx.webkit.WebViewAssetLoader?**
> Context: an SDK-direct build (no Gradle, no dependency
> resolver) loads its bundled web app from
> https://appassets.androidplatform.net/assets/… and serves the
> tree from a hand-rolled shouldInterceptRequest handler — the
> same reserved domain and interception point WebViewAssetLoader
> uses internally. Observed: state fetch (relative
> data/state.json) renders under this origin in an older AOSP
> WebView where a file:// origin + ACAO:* interception failed.
> Question: are there behavioral differences that matter —
> range requests, mime/charset defaults, path handling,
> error semantics — between the hand-rolled handler and the
  androidx class?

**Not posted, reason stated:** the write leg is live (all 10
scopes verified at preflight) and the miss is genuine — but the
atom the ASK would pose is already answered for our purposes by
firsthand fleet evidence (attempt 3 renders; the fidelity
question is now academic for this build, and the deciding leg
is a device smoke, not a literature question). Posting a
question we no longer need answered would spend the commons'
attention against the template's intent. The draft stays here
for the cycle where a difference actually bites — if one does,
it posts as-is with the observed difference added.

## Outcome stamp (2026-11-03, later the same day)

The deciding leg ran. Attempt 4 stamped the formal gate PASS
(run 41670971342, artifact 13248561510; repro 41670956811 RED
as required), and the owner's 0.1.3 device smoke PASSED on the
build of record — **issue #4276 is CLOSED by D1 adjudication,
both legs green.**

Per the kill-or-prove bound stated in §1/§5, the verdict flips:

**INCOMPLETE → CORROBORATED.** The appassets claim is proven
for both populations it was bound to: the emulator's older
WebView (attempt 3 substance, attempt 4 form) and the owner's
hardware WebView (0.1.3 device smoke). The one defect the smoke
did surface — an FSRS receipt reading "in NaN day(s)" — is a
caller-contract bug in the web bundle's grade path (issue
#4461), unrelated to asset serving; it does not touch this
verdict.
