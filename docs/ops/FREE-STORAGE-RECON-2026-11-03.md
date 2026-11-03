# Free Storage + ML Storage Recon — 2026-11-03

Owner spark (2026-11-03, via main): "Awesome free storage && ML Storage && ..." —
catalogue the free-storage landscape the way the provider enumeration
catalogued providers. **Catalogue pass only: no signups were made.** Terms
were read firsthand from vendor pricing/docs pages on 2026-11-03; fleet
state comes from fleet records plus one live account read (Drive).
Machine-readable rows: `ops/free-storage/free-storage-registry.json`
(schema `storage-registry/v1`) — the storing lanes (backup · podium · ML)
consume the registry; this note is the reasoning behind it.

## The corpora this is fitted against

- **Podium datasets** — competition dataset drops: public, citable,
  dataset-shaped, up to hundreds of GB.
- **ML datasets (compiling)** — the monorepo's uncompiled dataset material:
  large, growing, privacy-mixed; needs a private plane first.
- **Session exports** — session-history/chat-export corpora: JSON-shaped,
  privacy-sensitive, private-only.
- **Evidence media** — screen recordings, device frames, run artifacts:
  media files, public-as-receipts posture.
- **Backup plane** — repo mirrors and append-only snapshots (owner rule:
  nothing is deleted; redundancy before anything moves).

## Headline results

| Candidate | Class | Free allowance | Card | Fleet state |
|---|---|---|---|---|
| Backblaze B2 | object | 10 GB permanent, egress ≤3× stored free | **none** | no account |
| Cloudflare R2 | object | 10 GB-month + ops, egress free | **CARD-GATED — CLOSED** | token exists; R2 not enabled |
| Storj | object | none permanent (30-day trial, 25 GB) | none (trial) | no account; **vendor Chapter 11** |
| Hugging Face Hub | ML hub | public best-effort (~5 TB impactful), **private 100 GB** | none | **account exists; token read-scoped** |
| Kaggle | ML hub | 200 GB/dataset; 200 GB private quota | none | no account |
| Zenodo | archive | 50 GB/record, DOI | none | no account |
| OpenML | ML hub | quota NOT_ESTABLISHED | none | no account |
| Internet Archive | archive | items ≤500 files/500 GB | none | no account |
| GitHub Releases | archive | asset <2 GiB, no total documented | none | **in use** |
| GitHub LFS | object | 1 GB + 1 GB/mo | none | available, not a plane |
| GitLab free | archive | 10 GB/project | not established | **mirror in use** |
| Google Drive | connected | 15 GiB account-wide | none | **connected — ≈1 GiB headroom** |
| Dropbox | connected | NOT_ESTABLISHED | none | connected, quota unchecked |
| Neon | DB-adjacent | 1 GB/project DB (20 GB total) + 5 GB object/project | none | **live (lane-events)** |
| Supabase | DB-adjacent | 500 MB DB + 1 GB files | none | not established fleet-side |

## Stamps that matter

- **R2 is CARD-GATED, closed class.** Activation goes through a dashboard
  checkout requiring a payment method on file; the API returns error 10042
  until then (Cloudflare billing docs + firsthand fresh-account reports).
  Per the owner card rule it is never routed around. Its 10 GB free tier is
  recorded, stamped, and skipped.
- **Storj has no permanent free tier anymore** (discontinued 2024; what
  remains is a 30-day trial), and Storj Labs filed Chapter 11
  reorganisation on 2026-07-26. Trial-class + vendor-risk: never a sole
  copy, not a backup leg.
- **Drive is effectively full.** Live read 2026-11-03: 15 GiB quota,
  15,013,242,745 B used account-wide (Drive files 2,295,747,883 B) ⇒
  ≈1 GiB headroom. Owner recordings already land there; it cannot take a
  bulk leg until space is freed.

## Fit, per corpus

- **Podium datasets:** Kaggle primary (200 GB/dataset, competition-native,
  citable, versioned) + Zenodo for DOI-minted frozen drops (50 GB/record) +
  HF public for community-facing sets.
- **ML datasets (compiling):** HF private (100 GB) is the only large free
  *private* plane in the set — the fleet account exists, but the provisioned
  token is read/inference-scoped; a write-scoped token is the one
  provisioning act between here and use. Chunked GitHub releases (≤2 GiB
  parts, checksummed) cover public artifacts at any total size; B2's 10 GB
  is a small S3-shaped overflow.
- **Session exports:** private-only ⇒ HF private or B2. Never the
  public-by-design hubs (Kaggle/OpenML/Archive.org).
- **Evidence media:** GitHub Releases (the fleet's existing release-of-record
  pattern) + Internet Archive for permanent public copies.
- **Backup plane:** GitLab mirror (already a leg) + Archive.org snapshots
  of public artifacts + B2 10 GB for small append-only sets. Free storage
  does not change the redundancy rule: no corpus moves until a second copy
  exists.

## Honest gaps / NOT_ESTABLISHED

- Dropbox connected quota (connector's reviewed tools do not expose it).
- OpenML storage quota (no published figure found).
- GitLab card gate (mirror already exists; gate moot for the current leg).
- B2/R2 durability figures are vendor design claims, not measurements.

## Next acts (none taken on this pass)

1. HF write-scoped token (provisioning) ⇒ unlocks the ML-datasets plane.
2. B2 account (no card) ⇒ unlocks the S3 overflow/backup leg.
3. Zenodo + Archive.org accounts (no card) ⇒ unlocks DOI drops + permanent
   evidence archive.
4. Kaggle account (no card) ⇒ podium dataset lane.
Each is a separate owner-visible provisioning step, per the freemium-prep
doctrine (wire in-repo first, then sign up).

## Addendum 2026-11-03 — extensions ①②③④ (registry 15 → 48 rows)

Leads pass: simon987 + all-the-data awesome-datahoarding lists mined.
Reddit r/LinuxTeck thread read still pending (browser task, read-only);
failure modes below come from vendor terms + secondary practitioner reads.
Reddit haul folds in as a follow-up annotation, not a blocker.

### ① MEGA — the encrypted private plane

20 GB free, permanent while active; no card at signup; zero-knowledge E2E
(client-side encryption, user holds keys). Automation: MEGAcmd CLI
(Win/Mac/Linux) + open SDKs/clients; rclone as third-party transport.
Transfer quota: MEGA publishes NO fixed free figure (secondary reads vary
~1 GB/day to ~5 GB/month); over-quota downloads throttle/pause.
Dormancy, read firsthand from the Help Centre page (updated 2026-06-19):
free account itself never expires, but inactivity triggers warning emails
and eventual DATA deletion — whole process takes at least 10 months from
last activity; any login/app use resets it. Over-storage: view-only lock
after 30 days, deletion after 45 more (secondary). Achievement bonuses
(+5 GB each) expire after 365 days — never counted as base allowance.
Fit: BEST encrypted private fit for session exports/small archives;
never a sole copy (dormancy + transfer quota); not a public plane.

### ② P2P / decentralized — durability frame

In this class "free" means bytes live where someone pins or seeds them.
Stamp per row: who holds bytes · persistence mechanism · keep-alive cost.
- WebTorrent: browser BitTorrent over WebRTC (Desktop bridges to TCP/uTP
  swarms). Swarm-only; transport encrypted, CONTENT plaintext to peers —
  public-by-default, no content encryption.
- BitTorrent Speed / BTT (TRON variant): 2018 TRON acquisition, BTT 2019.
  Bidders pay BTT for speed, seeders earn for staying — an incentive, not
  a persistence guarantee. Content still public-by-default.
- S5 on Sia: content-addressed layer over Sia; s5-rs v1.0.0-beta.1 (Nov
  2025, Foundation grant complete). Sia contracts = collateral-backed
  while funded; S5 FS layer = E2EE snapshots/sharding/sync over untrusted
  nodes. Base blobs NOT auto-encrypted — state the layer per use. No
  ordinary free tier: "free" = self-hosted node or community pinning.
  Sia storage ~$2/TB-month class (secondary).
- Iroh (n0-computer): BLAKE3 addressing, QUIC/TLS 1.3, BlobTickets
  (hash + node + size). Transport encrypted; blobs NOT encrypted at rest
  by default; anyone with a ticket fetches. No built-in pinning network —
  provider node must stay online.
- IPFS: pin-or-gone. Adding a file does NOT replicate it. Retrieval
  evidence (secondary practitioner reads): dedicated gateways sub-second
  to ~500 ms; public gateways 1–5 s typical; GB+ files slow/unreliable
  over public gateways; gateway dependence partially re-centralizes.
  Managed pinning ~$15/TB-month class.
- Pinata free: 1 GB, 500 files, 10 GB bandwidth, 10K req/month, 1 gateway.
  Paid Picnic $20/month = 1 TB. Terms carry no uptime guarantee.
- Filebase free: 5 GB pooled (S3 + IPFS), 100K Class A + 1M Class B ops,
  S3 egress free, no card (comparison reads). Sia-network buckets have NO
  free tier. Pinned-file cap reads vary 500–1,000.
- web3.storage / Storacha: WINDING DOWN — do not start new pins.
  Team joined Filecoin Foundation Apr 2026; w3s.link gateway shut
  2026-05-31 (project ADR source).
- Academic Torrents: free account; publisher seeds. 400+ TB claimed.
  Webseed URLs backstop swarms. BEST fit for very large public sets.
- Syncthing: self-host mesh anchor. Bytes on fleet devices, transport
  encrypted, at-rest = device's own. Private sync, not public distribution.
Fleet split: PUBLIC artifact distribution (datasets, app packages,
snapshots) = fit; private storage = only MEGA + S5-FS (encrypted legs).
Transport encryption is NOT content privacy — stated per candidate.

### ③ Quant + ML data sources — SOURCES, not storage (trading freeze untouched)

Quant: EDGAR (free, no key, User-Agent required, ≤10 req/s, bulk ZIPs,
public domain — cleanest) · FRED (free key, 120/min; TERMS TRAP: current
Services Terms reportedly bar AI/ML training use + caching/archiving —
re-read live terms before ML use; older API terms lack the clauses) ·
Stooq (free bulk daily/hourly/5-min; personal-use-only, redistribution
needs consent; automation fragile 2026 — JS proof-of-work, scripted CSV
denied, pandas-datareader reader removed Jun 2026) · Dukascopy (free
tick→monthly CSV, 60+ instruments, 2003–2006 earliest, per-day downloads)
· HistData (free M1/tick from 2001; redistribution terms NOT_ESTABLISHED;
bulk API paid) · Binance Vision (free, no key, daily/monthly ZIPs +
CHECKSUMs; Binance.US terms bar specified commercial uses) · DoltHub
(public DBs free any size; private first 100 MB free, then paid).
ML: UCI (570+ sets, ~86% CC-BY 4.0, per-set DOI) · Common Crawl (300B+
pages, 10+ PB; HTTPS free no account, S3 Requester Pays + rate limits
since Nov 2023; content inherits page copyrights) · LAION-5B (5.85B
pairs, INDEX of URLs + alt text, not hosted media; reconstruct via
img2dataset) · Dolma (3T tokens; ImpACT license — contact + intended-use
agreement, NOT clean open source) · RedPajama-1T (1.2T tokens, 2.67 TB;
Apache 2.0 covers the MODELS, dataset licenses inherited) · HF Datasets
(source-role row; licenses per card) · Papers With Code (index only, no
storage) · DagsHub (free 20 GB per pricing page; per-repo doc figures
vary 10 vs 100 GB — flagged, pricing governs) · ModelScope (43k+ public
datasets counted Sep 2026; storage quota NOT_ESTABLISHED) · lakeFS
(tooling row only — versioning layer over your own object store).

### ④ Openness barter — public access is the price

EXPLICIT (application/curation): AWS Open Data Sponsorship (AWS pays
storage + egress, 2-year term renewable; application + Registry entry +
docs; FLEET BLOCKER: needs an AWS account — creation deferred pending
explicit owner approval) · Google Public Dataset Program (Google pays
BigQuery storage; readers pay queries, first 1 TB/month free; tabular
shape only; no SLA; self-serve public sharing is NOT barter — you pay) ·
Azure Open Datasets / Planetary Computer (Microsoft pays storage;
curated onboarding, no open application found; Pro bring-your-own-data
is a SEPARATE paid service; free Hub retired).
STRUCTURAL (public = free by design): Harvard Dataverse (free worldwide;
1 TB per researcher, 2.5 TB Harvard; 2.5 GB/file; DOI; default CC0) ·
data.world (public projects/datasets unlimited incl. free; REACH CAVEAT:
community content moved behind a login wall — "public" now means
account-holders, not the open web; per-dataset max NOT_ESTABLISHED) ·
plus base-registry members Kaggle, HF public, Zenodo, GitHub, Internet
Archive, OpenML, and amendment members DoltHub public, DagsHub public.
Fleet pairing: podium datasets = publication-eligible NOW; compiling ML
datasets = candidates AT COMPILE (license + privacy review then);
session/telemetry corpora = PRIVACY-HELD, never barter candidates absent
an explicit owner ruling.

### Amended fit summary

- Private encrypted plane: MEGA 20 GB (dormancy clock) + S5-FS (contract).
- Public distribution at zero marginal cost: IPFS pins (Pinata 1 GB +
  Filebase 5 GB) for small artifacts; WebTorrent/Academic Torrents for
  large public sets; barter programs for DOI-grade permanent sets.
- Quant/ML corpus sources above are inputs to the podium pipeline, not
  storage legs; license traps (FRED, Stooq, Dolma, Common Crawl
  inheritance) gate compile-time use.

## Addendum 2026-11-03 — ③ re-send coverage check

Main re-sent brief ③ (quant/ML-specific) after #4611 landed. Audit vs
master registry (48 rows, blob b8a8f59a): every re-send item maps to a
landed row; no new rows needed.

Quant → rows:
- SEC EDGAR bulk data → sec-edgar (nightly bulk ZIPs + JSON APIs;
  public domain; real-time as filed).
- FRED → fred (free key, 120/min; AI-training + caching terms trap).
- Stooq → stooq (bulk daily/hourly/5-min; personal-use-only; 2026
  automation fragile).
- Dukascopy/HistData class → dukascopy + histdata (tick→monthly CSV;
  M1/tick from 2001).
- Exchange public data archives → binance-vision (daily/monthly ZIPs +
  CHECKSUMs, no key). NOTE: Binance Vision is the verified bulk-archive
  exemplar; no second bulk archive verified on this pass — other
  exchanges' API-only surfaces are not counted as archives.
- DoltHub → dolthub (public DBs free any size; git-for-data).
- Open market datasets on the ML hubs → kaggle (base row, ml-hub class,
  200 GB/dataset) + hf-datasets-source (datasets-server API, Parquet
  endpoints). Market datasets live ON these hubs as dataset content;
  no separate row — the hub rows govern.

ML → rows:
- Common Crawl → common-crawl (monthly crawls; HTTPS free, S3
  Requester Pays).
- AWS Open Data Registry → aws-open-data-sponsorship (barter row doubles
  as source row: Registry entry + S3 access described there; sponsored
  datasets incl. petabyte class). Cadence + license are per-dataset on
  the Registry, not a single figure — correctly unstated as a global.
- Google public datasets → gcp-public-datasets (barter row doubles as
  source row: BigQuery public-data project, first 1 TB/month queries
  free; tabular shape only; no SLA). Cadence + license per dataset.
- UCI repository → uci-ml-repo (per-set DOI; ~86% CC-BY 4.0).
- Papers With Code → papers-with-code (index only, no storage).
- LAION/Dolma/RedPajama-class → laion-5b + dolma + redpajama (index vs
  ImpACT vs inherited-license notes as landed).
- ModelScope → modelscope (quota NOT_ESTABLISHED, honestly).
- DagsHub → dagshub (20 GB pricing page governs over varying per-repo
  docs).
- lakeFS-class versioning → lakefs (tooling row only, not capacity).

Boundary reaffirmed: cataloging only; trading-lane freeze untouched.

## Addendum 2026-11-03 — ① re-send coverage check

Main re-sent brief ① (MEGA) after #4611 landed. Audit vs master
registry (48 rows, blob b8a8f59a): row mega already answers all five
brief fields; no row change needed. Fresh re-verification 2026-11-03:

- Free allowance: 20 GB, permanent while active; achievement bonuses
  +5 GB each, expire after 365 days (never base). Confirmed by 2026
  guides + the original store-listing read.
- Transfer quota: MEGA publishes NO fixed free figure; secondary reads
  cluster ~5 GB/month (one read: monthly quota ~5 GB with throttling
  past it; older reads ~1 GB/day). Row range stands.
- Card gate: none — free plan $0, no card at signup (original
  store-listing read).
- API/automation: MEGAcmd CLI (mega-put / mega-get / mega-sync,
  mega-cmd shell; Win/Mac/Linux packages) + open SDKs/clients; rclone
  third-party. Confirmed fresh.
- Dormancy/deletion: Help Centre "Does my MEGA account ever expire?"
  (updated 19 June 2026, re-read fresh): free account has no expiry
  date; inactivity brings regular warning emails; the whole deletion
  process takes at least 10 months from last activity; only data is
  deleted, the account is kept; any login/app use stops it; Pro exempt.
  SHARPENING: the companion Help Centre page advises "log in at least
  once every 3 months" — fleet practice is quarterly logins; the
  10-month figure is the deletion-process bound, and the 3-month figure
  is the ToS termination option + notice. The row already carries both
  figures; the operational rule is quarterly, not 10-monthly.
- Fit unchanged: BEST encrypted private plane for session exports and
  small archives; never a sole copy (dormancy + transfer quota).

Boundary: catalog pass only, no signup; fleet_state stays "no account".

## Addendum 2026-11-03 — ② re-send coverage check

Main re-sent brief ② (P2P/decentralized) after #4611 landed. Audit vs
master registry (48 rows, blob b8a8f59a): every brief member maps; all
10 P2P/self-host rows carry durability_frame (holds_bytes ·
keep_alive · persistence) + a per-candidate encryption field + a fit
split (podium_datasets public vs private legs). No new rows; two small
row refinements in this PR (Filebase cap, IPFS cold-vs-cached).

Members → rows:
- WebTorrent family + desktop-client relatives → webtorrent (browser
  WebRTC + Desktop bridge to TCP/uTP swarms) + bittorrent-speed-btt
  (uTorrent/BitTorrent clients). Standalone classic clients are
  transports, not storage — no separate row; they hold bytes only as
  swarm members.
- TRON variant → bittorrent-speed-btt (2018 acquisition, BTT 2019,
  bid-for-speed / seed-for-reward; incentive, not persistence).
- S5 on Sia → s5-sia (protocol + s5-rs Rust impl v1.0.0-beta.1 + Sia
  blog spotlight, as landed).
- IPFS + pinning economics → ipfs-protocol + pinata + filebase +
  web3storage-storacha (winding down, do not start pins).
- Iroh → iroh (n0-computer stack; tickets are bearer tokens;
  provider must stay online).
- Leads-pass extras → academic-torrents (webseed-backed swarms) +
  syncthing (private device mesh).

Encryption, per candidate, never assumed: NONE at content layer for
WebTorrent, BTT, IPFS, Pinata (private = Enterprise paid), Filebase
IPFS leg, Storacha, Academic Torrents; transport-only for Iroh
(QUIC/TLS 1.3) and Syncthing (TLS); E2EE only on the S5 filesystem
layer (base blobs unencrypted unless FS used). Private fit therefore
exists ONLY for S5-FS (encrypted), the Syncthing mesh, and the Filebase
S3 leg (small) — everything else is public-distribution fit.

Fresh re-verification 2026-11-03:
- Pinata tier re-confirmed (own blog + Oct 2026 review): 1 GB / 500
  files / 10 GB / 10K req / 1 gateway; Picnic $20 = 1 TB; no uptime
  guarantee; private IPFS = Enterprise. Card gate: the free signup
  flow shows email activation with no card step in signup guides —
  gate stands as none; no explicit vendor "no card required" sentence
  located, flagged as the softest field in the class, not hidden.
- Filebase pinned-file cap resolved to 500 (Oct 2026 review: 5 GB
  shared, 500 pinned files, 10 GB IPFS egress) — the row's 500–1,000
  variance flag is retired by the edit in this PR.
- Retrieval speed, r/ipfs lead: the r/ipfs thread itself was NOT
  directly read this pass (Reddit text fetch blocked; search surfaced
  forums/docs/comparisons instead). Evidence now rests on Pinata docs
  (public gateways "naturally slower" under load; dedicated gateways
  fast via CDN), ProbeLab continuous TTFB measurement (fastest public
  gateways under 100 ms P50 on cache hits, Frankfurt; w3s.link
  +300–350 ms P50 on subdomain redirect), and the arXiv IPFS
  evaluation (3/4 EU retrievals under 2 s for 0.5 MB incl. lookup;
  gateway caching 76% under 250 ms). Refinement to the row: the 1–5 s
  public-gateway band is cold/uncached content and large files;
  popular cached content is routinely sub-second. Managed-pinning
  ~$15/TB-month class re-confirmed by an independent comparison.
- Managed-pinning economics + pin-or-gone frame unchanged.

Boundary: distribution of PUBLIC artifacts only, except the three
encrypted/private legs above; catalog pass only, no accounts, no pins
held.
