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
