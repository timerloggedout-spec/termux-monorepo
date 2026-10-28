# Linguist Admin Panel — census, layers spec, acceptance record

Owner lane: Linguist Admin Panel (layers & deploy coordination).
Pipeline: substrate → prototype → re-pin → deploy, all landed 2026-10-27.

## Chain of record

| Stage | PR | Merge SHA (history-scan + landed-content verified) |
|---|---|---|
| Substrate feed | #1864, #1868 | `29f4372ea2ee`, `1a9f84940d50` |
| Prototype | #1863 | `976de76d86ee` |
| Re-pin to landed feed | #1891 | `bf837b1095df8bed` |
| Shell integration (deploy) | #1892 | `06b981405275c123` |

Contracts: `docs/ops/LINGUIST-PANEL.md` (viz) + `docs/ops/LINGUIST-PANEL-FEED.md`
(substrate). Feed: `apps/help-wanted-dashboard/data/linguist-panel-feed.json`
(schema `linguist-panel-feed/v1`, 15 families / 288 entries enumerated /
7,575 total incl. count-only).

## Census gaps found 2026-10-27 (all closed by #1891)

- **G1 path:** prototype fetched `./data/linguist-feed.json` — 404 verified;
  landed feed is `linguist-panel-feed.json`.
- **G2 wrapper:** prototype read `feed.data.*`; landed feed is flat
  (renderer fix: `feed.data ?? feed`).
- **G3 table shape:** prototype expected entry `table {from:to}`; feed
  carries family `table [{from,to}]` on the 2 char families only
  (renderer fix: hoist family table to a synthetic char entry,
  admin-excluded; array `to` → first variant).
- **G4 direction:** prototype used raw `direction`; feed logic field is
  `direction_panel` (`both|forward` transform; `reverse|null` =
  match + admin only).

Substrate required no change: entries carry `family_id` / `match` /
`match_variants` / `round_trip_verified` on 288/288; `sample_texts[4]`,
`honesty_rules[5]` present.

## Layers switch — spec (owned by this lane)

Layers = family `kind` panel enum, 5 layers:

| Layer | Families | Entries |
|---|---|---|
| cipher | 1 | 32 |
| compression | 2 | 60 |
| leet | 5 | 88 |
| notation | 4 | 47 |
| other | 3 | 61 + 7,287 count-only |

Rules: two-level toggle — layer master (tri-state: all/some/none) ∧
per-family checkbox; effective enabled = layer ∧ family.
`archwiz-pointer-index` (7,287, `entries_included: false`): row visible,
toggle disabled, badge `count-only 7,287 — not enumerated`, never spans.
Definitional families (`direction_panel: null`, notation): span matching
+ admin browse only, no transform columns.

## Acceptance

`scripts/linguist/linguist_panel_acceptance.py` — static gate (G1–G4,
feed sanity, layers, count-only guard, feed-absent state). Against the
pre-re-pin page it failed exactly G1–G4 + layers; PASS 8/8 on the
#1891/#1892 landed page (3 early checker false-positives were fixed in
the checker — the implementation was correct on code read).

Criteria A–D (viz node sim, tests 4/4): (a) all layers off → no columns
or spans, admin still browsable; (b) leet-only → char transforms render
(`abe` → `4b3`); (c) notation-only → spans yes, transform no;
(d) feed-absent state retained on fetch failure. Real-feed sim:
sample 0 → 23 spans, 9 transform families, `leet speak` → `l337 5p34k`.

Stage-3 integration acceptance (PR #1892, head `6d33ab2a`): renderer
script byte-identical pre/post (13,249 B, sha256
`a65000081116e34011ceb0a5f11d6cef291006d0eaec9d8fff99668e5d0a59e1`),
16 element ids unchanged, `linguist.html` diff +10/-0 chrome only;
nav on all 13 other pages + Countdowns link into linguist (closes the
PR #1882 skip); sitemap loc; Admin inventory row (`admin.html`);
no feed/contract files touched; hygiene + smoke + contracts green.

Telemetry disposition: `Targeted telemetry regression tests`
(help-wanted-telemetry-tests) failed on the #1892 head — A/B evidence
on PR #1892 (comment 6459013881): 1 failed / 51 passed **identical**
with the diff and on pristine master (`test_cadence_emits_lag_failure_incidents`,
the cadence pin; fix owner = cadence/dispatch-tree lane). Independent
of this workstream; conditional PASS activated on that evidence.

Live verdict (Web Design lane): `linguist.html` HTTP 200, 19,787 B
(matches the landed blob size verified by this lane), shared chrome +
feed wiring serving.
