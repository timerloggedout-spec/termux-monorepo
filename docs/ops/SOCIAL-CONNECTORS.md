# Social Connectors — RECON 🏅 + Build State (2026-10-31)

`[MUSEai]@{role:{social-connectors}}` ∘ owner order 2026-10-31 ∘ model = `custom.github-pat` (vault credential + local helper + connector doc ⇒ ∅ per-action approval cards).
Sources: official developer docs (TikTok direct-read; Meta/X/WhatsApp cross-checked ≥2 dated secondary guides vs official paths ∵ provider doc pages ¬ search-indexed this session — re-verify in-console at provisioning). Claims carry verdicts; NOT_ESTABLISHED ≠ absent.

## ⚠️ X — PARK conflict (surfaced, ¬ silently resolved)

Standing park (owner, 2026-10-29, fleet-wide, X account access) ∧ X listed in the 2026-10-31 recon order ⇒ **recon-only**. ∅ wiring, ∅ credential request. Resume requires owner un-park via main. Tech verdict independent of park: ¬ clean (below).

## Recon table

| Platform | Route ∘ posting auth | Vault fit | Gates | Limits / cost | Verdict |
|---|---|---|---|---|---|
| FB Pages | Graph v26.0 `graph.facebook.com` (+`rupload.facebook.com`) ∘ Page token, `pages_manage_posts`+`pages_read_engagement`+`pages_show_list` | ✓ single bearer; Page token (from long-lived user token) non-expiring; System-User token alt | own Pages = Standard Access ⇒ ∅ App Review, ∅ Business Verification; CREATE_CONTENT task req'd | BUC 4,800×engaged-users/24h; Reels 30/day | **CLEAN ⇒ BUILD** |
| Instagram | Content Publishing, 2-step container ∘ Route B (FB Login) = Page token, `instagram_content_publish`; Route A (IG Login) = `instagram_business_content_publish` | ✓ Route B by inheritance; ✗ Route A (60d rotating) | own-use ∅ review | publish cap docs conflict 50 vs 100/24h ⇒ poll `content_publishing_limit`, ¬ hardcode | **CONDITIONAL ⇒ build as FB extension; prereq IG Professional + Page link = NOT_ESTABLISHED** |
| Threads | `graph.threads.net/v1.0`, 2-step ∘ `threads_basic`+`threads_content_publish` | ~ single bearer, 60d; refresh returns NEW token ∧ ∅ vault write-back ⇒ dies day-60 w/o manual re-vault | tester route ∅ review | 250 posts/24h/profile | **CONDITIONAL ⇒ buildable + ~50d re-vault ritual** |
| WhatsApp | Cloud API `graph.facebook.com` ∘ permanent System-User token, `whatsapp_business_messaging`+`whatsapp_business_management` | ✓ single bearer, expiry Never | template approval + display-name approval; biz-verify to scale; 24h window (free-form in-window only, else approved template); opt-in req'd; payment method req'd | start 250 unique users/24h, 80 msg/s/number; US per-delivered: marketing $0.025, utility/auth/service $0.0034 | **CLEAN (outbound) ⇒ BUILD; blockers business-side (WABA/number/payment = ∅ yet)** |
| TikTok | Content Posting API v2 `open.tiktokapis.com` ∘ `video.publish`/`video.upload`, OAuth2 user-ctx | ✗ `client_key`+`client_secret` multi-secret, cross-domain OAuth, 24h token + rotating refresh | **audit: unaudited ⇒ SELF_ONLY ∧ ≤5 users/24h ∧ private accounts only** | init 6/min/token; ~15 posts/24h/creator | **BLOCKED** |
| X | API v2 `api.x.com/2` `POST /2/tweets` ∘ `tweet.write`+`media.write`+`offline.access` | ✗ posting = OAuth2 user-ctx (2h, cross-domain) ∨ OAuth1.0a 4-secret signed; bearer = read-only; hosted MCP ∅ post tool | Developer Agreement + prepaid credits (card) | $0.015/post, $0.20 w/ URL; 100/15min/user | **⛔ PARKED (recon only) ∧ ¬ clean** |

Structural finding: **∅ vault write-back** — refresh endpoints return a new token the helper cannot persist ⇒ rotating-token platforms (IG-A, Threads, TikTok, X) need manual re-vault cadence; non-expiring tokens (FB Page, WA System-User) are the only set-and-forget fits. ∅ official posting MCP exists for FB/IG/Threads/TikTok (Meta MCPs = Ads, Social-Tech/devtools, WhatsApp-Business-Tools-setup; X MCP = read-only for posts) ⇒ REST helpers everywhere.

## Stock ⇒ custom Δ (firsthand 2026-10-31)

- FB stock (`facebook_cli`): connected, Pages = Dream In Production ∧ Receipts Count (fb-c Code, Not Card absent ⇒ still uncreated); covers personal+Page publish BUT per-action approval cards ⇒ custom Δ = card-free Page posting + repo-automation reach.
- IG stock: full surface, accounts=[] (unlinked) ⇒ stock path unprovisioned. Threads stock: publish surface, accounts=[].
- WhatsApp stock: personal chat-connection provider only (status unlinked); custom = separate business identity/broadcast surface, ∅ identity overlap.
- TikTok/X stock: ∅.

## Others scan (report-only; ∅ build without owner word)

BUILD-candidates: **Telegram** (Bot API, 1 BotFather token, ∅ review; bot-as-channel only) > **Mastodon** (`POST /api/v1/statuses`, 1 long-lived bearer, ∅ review; needs instance+account decision) > **Discord webhook** (1 URL-token; fleet account is a user account ⇒ self-bot = ToS ✗, webhook/bot only) > **Bluesky** (app password, ∅ review, session-cache care).
Gated queue: YouTube (OAuth multi-secret + compliance audit; unverified = private-only uploads) > LinkedIn-personal (60d token; org = Community Management review) > Pinterest (Standard review) > Reddit (pre-approval + commercial agreement). Skip: Snapchat (∅ organic posting API) ∧ Twitch (∅ posting surface).

## Provisioning census (a78e43e6, 2026-10-31, state-only)

Meta dev app = NOT_ESTABLISHED/∅ held · IG Professional+link = NOT_ESTABLISHED · TikTok dev app = ∅ · WABA = ∅ · X dev account exists (owner-created 2026-10-29, $0 pay-per-use) PARKED, `X_OAUTH2_*` shelved. Moniker census (ac8e5e6b) pending at record time; FB Page identities already registered (Dream In Production fb-a, Receipts Count fb-b).

## Build state (2026-10-31)

- `custom.meta-pages` SCAFFOLD LANDED (local connector dir): `connector.yaml` + `CONNECTOR.md` + `bin/meta_pages.py` (me/pages/page-post/page-feed/ig-account/ig-publish/ig-limit/get), py_compile ✓, **UNTESTED-LIVE** — connection ¬ registered; mint = provisioning item (Meta app ⇒ one-time owner OAuth exchange ∨ System-User token ⇒ vault entry, hosts `graph.facebook.com`+`rupload.facebook.com`, bearer_header).
- `custom.whatsapp` SCAFFOLD LANDED: `connector.yaml` + `CONNECTOR.md` + `bin/whatsapp.py` (send-text/send-template/templates/phone-info/get), py_compile ✓, **UNTESTED-LIVE** — WABA provisioning pending.
- Threads: helper deferred to provisioning (60d re-vault ritual decision rides with token mint). TikTok: ∅ build (blocked). X: ∅ build (parked).
