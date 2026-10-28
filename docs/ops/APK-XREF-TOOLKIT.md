# APK ↔ Repo Cross-Reference — toolkit (utility belt)

`[MUSEai]@{role:{reverse-engineering-toolkits}}` — owner order via the
Foundry lane (2026-10-28): this chat is the dedicated lane for the Reverse
Engineering category's toolkits / utility belts; this is the first belt,
built for the 2026-10-28 wave's 30 paired cross-reference briefs
(`-apk` issues #2064–#2123 in the #2063–#2123 range).

## Place in the category

| Layer | Home | Owner |
|---|---|---|
| Campaign / design charters | `docs/ops/WEB-REVERSE-ENGINEERING-CAMPAIGN.md`, `docs/ops/WEB-ADAPTER-FOUNDRY.md` | Foundry |
| Filings + findings forms, `apk-xref/v1` intake | `.github/ISSUE_TEMPLATE/apk-cross-reference*.yml`, `scripts/apk_xref/`, `docs/ops/APK-XREF-TEMPLATES.md` (PR #2140) | research-triggers |
| **This toolkit** | `ops/web_adapter_foundry/apk_xref.py` + `apk_signatures.json` | reverse-engineering-toolkits |
| Tests | `tests/test_apk_xref.py` | reverse-engineering-toolkits |

Probing keeps the owner's definition (2026-10-27): find the DOMs from
the request. For an APK the analogue is: find the endpoints, providers
and routes the artifact actually embeds or calls — from the artifact,
not from the source's claims about it.

## The four stages

```bash
# 1. Acquire — published artifact only, provenance recorded
python3 -m ops.web_adapter_foundry.apk_xref acquire \
  --source github-releases --repo SilentCoderHere/aihub --out artifacts/aihub
python3 -m ops.web_adapter_foundry.apk_xref acquire \
  --source f-droid --package-id com.example.app --out artifacts/app
#    sources: github-releases | gitea-releases (--gitea-url) | f-droid | direct-apk (--url)
#    Google Play is REFUSED as an acquisition source (no Play scraping).
#    Exit 3 + a sources-checked evidence list when nothing is published.

# 2. Extract — the artifact as published
python3 -m ops.web_adapter_foundry.apk_xref extract app.apk --out extraction.json

# 3. Claims — draft the repo side from the paired source tree
python3 -m ops.web_adapter_foundry.apk_xref scan-repo /path/to/repo --out claims.json
#    or hand-write claims in the same apk-claims/v1 shape
#    (ops/web_adapter_foundry/examples/apk-claims.example.json), including
#    the filing's claims_to_check lines — relagent #2123's local-only and
#    llama.cpp/Gemma checks are deterministic claim checks in the engine.

# 4. Cross-validate + emit findings in the template shape
python3 -m ops.web_adapter_foundry.apk_xref xref \
  --extraction extraction.json --claims claims.json \
  --target-id aihub --xref-issue '#2064' \
  --submitter 'reverse-engineering-toolkits{...}' \
  --out report.json --markdown findings.md
#    no artifact? close it WITH evidence instead:
python3 -m ops.web_adapter_foundry.apk_xref no-artifact \
  --target-id wraith --xref-issue '#2121' --submitter '...' \
  --sources-checked 'github-releases: no APK asset' 'f-droid: not listed' \
  --out report.json --markdown findings.md
```

## What extraction covers (stdlib-first)

- **Manifest** — a built-in binary AXML parser (string pool + typed
  attributes): package ID, version name/code, SDK levels, every
  `uses-permission`, components (activities/services/receivers/providers
  + authorities + exported), meta-data names, intent-filter deep links.
- **Endpoints/hosts** — DEX string tables (all `classes*.dex`) plus
  text assets scanned for URLs; hosts also credited from provider
  signature hosts named in strings and manifest deep-link hosts.
  Endpoints are reported host+path (query values never recorded).
- **Providers / trackers** — `apk_signatures.json`: host matches
  (exact / subdomain / `*.suffix`), string markers, embedded config
  files. Provider configs (e.g. `google-services.json`) contribute the
  provider id, the public project id, and key **names only** — secret
  values are never extracted, and config files are excluded from the
  string corpus for the same reason.
- **Feature signals** — llama.cpp / GGUF / ONNX / TFLite / MediaPipe /
  Whisper / WebView / … matched against strings, assets and native libs.
- **Classification** — deterministic `class:` / `provider:` /
  `tracker:` / `signal:` / `permission:` tags plus routes
  (`routes.api`, `routes.deeplinks`), so the wave's findings tag
  consistently instead of free-handing labels per app.

Where a standard tool is needed it is a corroborator, not a dependency:
`aapt dump badging` / apktool output can be diffed against this
extraction in CI, but the belt runs anywhere Python 3.10+ runs
(Termux, CI, remote) — the B160V law is respected by keeping all of it
light, pure-stdlib, and off the browser stack. Full decompilation
(jadx-class) is deliberately out of scope: cross-reference needs the
manifest/endpoint/provider surface, not recovered source.

## Cross-validation semantics

Both directions, per category (hosts, endpoints, providers,
permissions, features, package, trackers, signals):

- **repo → APK** — claimed in source, absent in the artifact.
- **APK → repo** — present in the artifact, not claimed in source
  (trackers and feature signals always surface here when unclaimed).

Freeform claims from the filing (`claims_to_check`) get deterministic
outcomes where the artifact can decide them — `supported` /
`contradicted` / `not-found` — and an honest `unchecked` where it
cannot. The local-only check is the relagent shape: external hosts or
endpoints in the artifact contradict a "pure local" claim; an INTERNET
permission alone downgrades it to not-found, never to supported.

Verdict follows the template set exactly: `match` /
`divergences-found` / `no-artifact-found`.

## The seam with the template set (PR #2140)

- The JSON report **is** an `apk-xref/v1` findings record — the form's
  keys verbatim. Extraction detail (classification, providers with
  evidence, trackers, provider configs, components) rides under
  extension keys; nothing renames a template field.
- The markdown report uses the findings form's headings verbatim, so
  `scripts/apk_xref/apk_xref_intake.py` re-parses it into the same
  record. This round-trip is verified: a toolkit-generated findings
  file fed through the intake parser reproduces every findings field
  losslessly (checked against PR #2140 as merged).
- One recorded divergence: the form's `artifact_source` enum includes
  `google-play` as a label; acquisition in this belt still refuses
  Play as a source. An artifact obtained by other means may carry the
  label; the belt will not scrape for it.

## Corpus caution

`extract` includes the DEX string corpus by default because
cross-validation searches it. That corpus is a working file from a
published artifact — share reports, not corpora; use `--no-corpus`
when an extraction must travel (feature checks then fall back to the
structured surface: hosts, endpoints, assets, libs).
