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

## Execution workflow (Actions)

`apk-xref-intake.yml` only records filings. Execution is
`.github/workflows/apk-xref-exec.yml` (owner ENV rule: swarm
execution runs in GitHub Actions' ephemeral runners — not on a VM,
not on a device), dispatched per filed request issue:

```
gh workflow run apk-xref-exec.yml -f issue_number=2273
```

The runner script `ops/web_adapter_foundry/apk_xref_exec.py` parses
the filing, then drives this belt: acquire (exit 3 = no artifact, an
evidence outcome) → extract → clone the target repo → scan-repo →
xref, or the no-artifact record when nothing is acquired. It files
the findings on the Findings form (the belt's own markdown render),
comments the verdict + findings link back on the request issue, and
uploads a findings-only evidence artifact (extractions carry the DEX
corpus, which does not travel).

One platform subtlety: issues created with a workflow `GITHUB_TOKEN`
do not retrigger other workflows, so the findings issue cannot wake
`apk-xref-intake`. The exec workflow therefore runs the same
deterministic intake parser itself and posts the record with the
intake workflow's own hash-dedupe marker — a later human edit
re-runs intake, which skips its duplicate.

## Acquisition routes (2026-11-01 alt-store pass)

Wired sources (`acquire` tries the filing's sources in order):

| source | channel | mechanics |
|---|---|---|
| `github-releases` | GitHub Releases | latest release carrying an `.apk` asset; repo may be filed as slug or URL (normalized) |
| `gitea-releases` | Gitea/Forgejo Releases | same shape via `/api/v1` |
| `f-droid` | f-droid.org | metadata API; F-Droid-rebuilt + F-Droid-signed binaries |
| `izzyondroid` | IzzyOnDroid repo (`apt.izzysoft.de/fdroid/repo`) | F-Droid-protocol v2 index (`index-v2.json`, verified live: 1,401 packages); binaries are **developer-built + developer-signed**, taken from upstream — a different trust class from `f-droid`, recorded in provenance (`repo_base`, `index_sha256` = the channel's per-file hash claim, next to the belt's own sha256 of the bytes) |
| `other-store` | alt-store fallback chain | tries `izzyondroid` then `f-droid` for the package id; the acquired provenance carries `via: other-store-><channel>` |
| `direct-apk` | a filed URL | refused outright when the host is `play.google.com` |

**KomiStore — no channel to wire (verdict).** Komi Store (formerly
GitHub Store) is a discovery/install layer over GitHub, Codeberg and
Forgejo *releases*: the bytes it delivers are the upstream release
assets themselves, already covered by `github-releases`/`gitea-releases`
byte-for-byte. There is no KomiStore artifact channel distinct from
its upstreams; its digest-verification idea is already belt behaviour
(every download is sha256'd; F-Droid-protocol channels also carry an
index hash claim for parity checks). A filing naming KomiStore maps
to the upstream repo's releases route.

**Aurora Store — the design question, answered honestly.** Aurora is
an unofficial Google Play *protocol client*, not a download URL: an
anonymous session is dispensed a Google account token by community
dispenser servers, then speaks the Play protobuf API (check-in,
purchase, delivery), and modern Play apps are delivered as split-APK
sets derived from bundles rather than one universal APK. None of
that fits this belt's stdlib, URL-route shape, and the dispenser
layer adds a third party's Google accounts to the trust path. The
belt's direct-Play refusal therefore stands, and `aurora` is **not**
a wired source: a Play-only target filed today resolves through the
wired alt channels (`other-store` chain) and, when none serves it,
the no-artifact record names the checked channels — that record is
the Aurora demand signal. Wiring Aurora for real is a separate
build (dedicated Play-protocol client + an owner ruling on the
dispenser trust posture), not an acquire-route patch.

**Channel parity.** Where two channels serve the same package, run
acquire per channel and compare: provenance `sha256` (belt-computed
over the actual bytes) per channel, plus `index_sha256` where the
channel publishes one. Byte-identical artifacts across channels hash
equal; F-Droid-proper vs developer-signed channels (IzzyOnDroid,
GitHub) legitimately differ for many apps because the signer/build
differs — parity claims must name the channels they span.
