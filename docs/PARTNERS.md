# Developer partners & referral ecosystem

Affiliate, referral, and gifted-usage lanes this project takes part in — the consolidated, deduplicated form of issue #574 ("Marketing Strategies Referrals"). One row per partner. The root README banner shows at most **four badges**; new partners get a row here first and a badge only when one rotates out. The landing page (https://timerloggedout-spec.github.io/) renders an "Ecosystem partners" grid from the **active** rows only.

## 1. Active lanes (tracked link live)

| Partner | Category | Offer | Link | Badge | Owner |
|---|---|---|---|---|---|
| CellCog | AI employees & agents (anchor) | 500 bonus credits on first purchase | https://cellcog.ai/invitation/l19hdRGY9dTh | `Powered by CellCog AI employees` (teal `2e7e7e`) — in banner | Marketing (Chloe) |
| Polsia | AI directory & intelligence | 500 extra credits (per #574 — verify on signup) | https://polsia.com/?ref=B5K7S8NL | — | Marketing (Chloe) |
| Manus AI | AI employees & agents | Invitation link (UTM-tagged) | https://manus.im/invitation/5MHU34UJRBOTVC6?utm_source=invitation&utm_medium=social&utm_campaign=system_share | — | Marketing (Chloe) |
| Grafana | Observability & cloud | Referral code `gr8WEigykKjVGTV` | https://grafana.com/auth/sign-up?refCode=gr8WEigykKjVGTV | — | Marketing (Chloe) |

## 2. Owned channels

| Channel | Use | Link |
|---|---|---|
| YouTube community post | Public listing of the referral lanes; edited continually | http://youtube.com/post/UgkxG7m4gdVolQ8V_JaP1vj62JSSWjMz-gfD |

## 3. Pipeline (named in #574, no tracked link yet)

Route per partner: referral/affiliate programme if one exists → otherwise gift-card / gifted-usage codes → otherwise direct contact (sales, marketing, developer-relations). Status moves to §1 when a tracked link lands.

| Category | Candidates | Route notes |
|---|---|---|
| Generative media | HiggsField, Kling AI, Suno (listed as "Sumo" in #574) | Gift-card redemption & referral programmes |
| LLMs & agent platforms | Moonshot AI (Kimi), Grok, Google, DeepSeek, GenSpark, FELO.ai, OpenRouter, OMNI, Devin.ai, Codex, BlackBoxAI, Dify, Tanka, Stepie, LikeClaw | Kimi: gift-card redemption codes |
| Cloud, hosting & infra | v0, Vercel, Render, Cloudflare, Firebase, Repl.it, Gitpod / Ona (app.ona.com), Tailscale, Tembo | v0: gifted-usage codes; Ona: coupons |
| Developer platforms & tools | GitHub, GitLab, Hugging Face, Hex, Brave | — |
| Retail gift cards | Google Play Store redeem codes | Gift-card redemption |

## 4. Support & sponsorship (addresses pending)

| Kind | Assets | Status |
|---|---|---|
| Cryptocurrency wallets | BTC, ETH, DOGE, WOWnero, DASH (more to follow) | Addresses not yet published — Operator adds them here |
| NFTs | — | Placeholder from #574 |

## Standing rules

- Continually append and implement this list "for resources replenishment" (#574).
- No referral or affiliate programme for a collaborator → begin direct contact (sales / marketing departments) and alternative gifted-usage routes.
- Banner cap: four badges, never grow it; rotate instead.

## Adding a partner

1. Add a row in §1 (or §3 while no link exists): partner, category, the offer in one line, the tracked link, badge (if any), and the owner.
2. Badge format: `https://img.shields.io/badge/<label>-<message>-<hex>?style=for-the-badge` (spaces as `_`, dashes as `--`).
3. If the partner belongs in the root banner, replace one of the four badges inside the `partner-banner` markers in `README.md`.
4. Mirror active rows into the `partners.items` block of `js/content.js` in the landing repo (Marketing owns copy; Engineering owns layout).
5. Open a PR against `master` citing the demo-portal proposal (`Implements: DP-00x`); both gates must be green.

Disclosure: partner links may be affiliate or referral links. New accounts signing up through them may receive promotional credits; terms and platform policies apply. Source of truth for the raw list: issue #574.
